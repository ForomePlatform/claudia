import json
import logging
import memcache
from h_memcache import MemCacheHandler


#def cacheConverter(data):
#    print('start')
#    cch = ClaudiaCacheHandler()
#    cch.clear()
#
#
#class ClaudiaCacheHandler:
#    def __init__(self):
#        self.mch = MemCacheHandler('localhost',  '11211',  'claudia',  3600,  1000)
#        self.maxPartSize = 500000
#        self.maxCountOfParts = 1000
#    
#    def getFreeTicket(self):
#        locks = self.mch.getValue('tickets')
#        if locks is None:
#            locks = []
#        print('keys: ' + str(locks))
#        for n in range(self.mch.mMaxLocks):
#            if str(n) not in locks:
#                locks.append(str(n))
#                self.mch.putValue('tickets',  locks)
#                return str(n)
#        print('Overflow of the cache: count of records is greater than ' + str(self.mch.mMaxLocks))
#    
#    def getValue(self, ticket):
#        print('Get.')
#        data = ''
#        for n in range(self.maxCountOfParts):
#            part = self.mch.getValue(ticket + '#' + str(n))
#            #if part is not None:
#                #print('Key: ' + ticket + '#' + str(n) + ': ' + str(len(part)))
#                #print('part: ' + part[:100])
#            if part is None:
#                if data == '':
#                    return None
#                else:
#                    return json.loads(data)
#            else:
#                data += part
#    
#    def putValue(self, ticket, value):
#        print('Put.')
#        data = json.dumps(value)
#        for n in range(self.maxCountOfParts):
#            part = data[n*self.maxPartSize : (n+1)*self.maxPartSize]
#            #print('Part ' + str(n) + ': ' + str(len(part)))
#            if part != '':
#                self.mch.putValue(ticket + '#' + str(n), part)
#                #print('Put len: ' + str(len(self.putValue(new_key + '#' + str(n)))))
#            else:
#                self.mch.mClient.delete(ticket + '#' + str(n))
#        if n < self.maxCountOfParts-1:
#            print('Overflow of the cache: size of a document is greater than ' + str(self.maxCountOfParts * self.maxPartSize))
#    
#    def checkout(self,  ticket):
#        for n in range(self.maxCountOfParts):
#            new_key = ticket + '#' + str(n)
#            #print('checkout: ' + new_key)
#            self.mch.checkout(new_key)
#    
#    def clear(self):
#        self.mch.mClient.flush_all()




# This class lets to save in a cache very big data for
# many users (tickets).
# It split the data into several parts such that every part 
# is an independed record in the cache.
#
# Example of a record:    { claudia#342#7 : <part of data>}
#
# Here "claudia" is a Namespace, "342" is a ticket, 
# "7" is a number of currant part of data of the ticket.
#
# List of currant tickets is saved in the cache like an ordinal record 
# and it survives after programm exit.

class ClaudiaCacheHandler:
    def __init__(self, Namespace, host='localhost', port='11211', 
                                            timeout=3600,  clear=1000):
        self.mClient = memcache.Client([host + ":" + port], debug=1)
        logging.info("Memcache at %s:%s" % (host, port))
        self.mNamespace = Namespace + "#"
        self.mTimeout  = timeout
        self.mClear = clear                         # Remove all empty ticket if tickets are too much (>mClear)
        self.maxPartSize = 500000            # Maximal size of one part of a ticket value
        self.maxCountOfParts = 1000        # Maximal count of parts of a ticket value

    def checkin(self,  ticket):
        tickets = self.getTickets()
        tickets.append(ticket)
        tickets = list(set(tickets))
        self.putValue('tickets',  tickets)
    
    def checkout(self,  ticket):
        tickets = self.getTickets()
        tickets.remove(ticket)
        self.putValue('tickets',  tickets)
        
    # Remove a ticket and all its data
    def removeTicket(self, ticket):
        for n in range(self.maxCountOfParts):
            key = self.mNamespace + ticket + '#' + str(n)
            self.mClient.delete(key)
        self.checkout(ticket)
    
    # Get list of tickets
    def getTickets(self):
        tickets = self.getValue('tickets')
        if tickets is None:
            tickets = []
        return tickets
        
    # Get a new unical ticket
    def getFreeTicket(self):
        tickets = self.getTickets()
        if len(tickets) > self.mClear:
            self.clearCache()
        for n in range(len(tickets) + 1):
            if str(n) not in tickets:
                self.checkin(str(n))
                return str(n)
    
    # Check all tickets and delete empty tickets
    def checkTickets(self):
        tickets = self.getTickets()
        for ticket in tickets:
            value = self.getValue(ticket)
            if value is None:
                self.removeTicket(ticket)
        self.putValue('tickets',  tickets)

    def getValue(self, ticket):
        data = ''
        for n in range(self.maxCountOfParts):
            key = self.mNamespace + ticket + '#' + str(n)
            part = self.mClient.get(key)
            if part is None:
                if data == '':
                    return None
                else:
                    return json.loads(data)
            else:
                data += part
    
    def putValue(self, ticket, value):
        if ticket != 'tickets':
            self.removeTicket(ticket)
            self.checkin(ticket)
        data = json.dumps(value)
        for n in range(self.maxCountOfParts):
            part = data[n*self.maxPartSize : (n+1)*self.maxPartSize]
            if part != '':
                key = self.mNamespace + ticket + '#' + str(n)
                if ticket == 'tickets':
                    self.mClient.set(key, part)
                else:
                    self.mClient.set(key,  part,  time=self.mTimeout)
            else:
                return
        print('Overflow of the cache: size of a document is greater than ' + str(self.maxCountOfParts * self.maxPartSize/1000000) + 'Mb.')
    
    # Remove all tickets in the cache
    def clearCache(self, clearAll=False):
        if clearAll:            # Clear all cache, not in this Namespace only.
            self.mClient.flush_all()
            return
        tickets = self.getTickets()
        for ticket in tickets:
            self.removeTicket(ticket)
    



if __name__ == '__main__':
    cch = ClaudiaCacheHandler()
    cch.clearCache()
