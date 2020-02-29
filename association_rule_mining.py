import mysql.connector
import time

def get_transactions_helper(transaction_database_id):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="devan",
    database="Apriori"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT `transactions`.transaction_id, `items`.id FROM `transactions` JOIN items ON `items`.id = `transactions`.item_id WHERE `transactions`.transaction_database_id = " + str(transaction_database_id) + " ORDER BY `transactions`.transaction_database_id")
    myresult = mycursor.fetchall()
    return myresult

def get_transactions(transaction_database_id):
    transactions = get_transactions_helper(transaction_database_id)
    d = dict()
    for t in transactions:
        transaction_id = t[0]
        item_id = t[1]
        d.setdefault(transaction_id, []).append(item_id)
    return d
    
def calculate_support(items, d, number_of_transactions):
    count = 0
    for transaction_id in d:
        found_all = True
        for i in items:
            if i not in d[transaction_id]:
                found_all = False
                break
        if found_all:
            count = count + 1
    support = float(count) / number_of_transactions
    return support

def self_join(_set, n):
    # join if n - 2 elements are same
    result = list()
    for i in range(len(_set)):
        for j in range(i + 1, len(_set), 1):
            count = 0
            for item in _set[i]:
                if item in _set[j]:
                    count = count + 1
            if count == n - 2:
                temp = list(set(_set[i]) | set(_set[j]))
                if temp not in result:
                    result.append(temp)
    return result

def combinations(_set, n):
    size = len(_set)
    indices = range(n)
    yield list(_set[i] for i in indices)
    while True:
        for i in reversed(range(n)):
            if indices[i] != i + size - n:
                break
        else:
            return
        indices[i] += 1
        for j in range(i + 1, n):
            indices[j] = indices[j - 1] + 1
        yield list(_set[i] for i in indices)

def generate_association_rules(frequent_set):
    association_rules = list()
    for item_set in frequent_set:
        counter = 1
        while counter < len(item_set):
            rule = list()
            rule.append(item_set[0:counter])
            rule.append(item_set[counter:])
            _rule = list()
            _rule.append(item_set[counter:])
            _rule.append(item_set[0:counter])
            if rule not in association_rules:
                association_rules.append(rule)
            if _rule not in association_rules:
                association_rules.append(_rule)
            counter = counter + 1
    return association_rules

def get_l1(d, number_of_transactions, minimum_support):
    l1 = list()
    for transaction_id in d:
        for item_id in d[transaction_id]:
            temp = list()
            temp.append(item_id)
            if (temp not in l1 and calculate_support(temp, d, number_of_transactions) >= minimum_support):
                l1.append(temp)
    return l1

def get_items(d):
    items = list()
    for transaction_id in d:
        for item_id in d[transaction_id]:
            if (item_id not in items):
                items.append(item_id)
    return items

def minimum_confidence_is_satisfied(rule, d, number_of_transactions, minimum_confidence):
    ex = list()
    ex.extend(rule[0])
    ex.extend(rule[1])
    combined_support = calculate_support(ex, d, number_of_transactions)
    left_support = calculate_support(rule[0], d, number_of_transactions)
    if left_support != 0:
        confidence = float(combined_support) / left_support
    else:
        confidence = 0
    if confidence < minimum_confidence:
        return False
    return True

def minimum_support_is_satisfied(element, d, number_of_transactions, minimum_support):
    support = calculate_support(element, d, number_of_transactions)
    if support < minimum_support:
        return False
    return True

def apriori(minimum_support, minimum_confidence, transaction_database_id):
    d = get_transactions(transaction_database_id)
    if d is None or len(d) == 0: return None
    number_of_transactions = len(d)
    candidate_set = get_l1(d, number_of_transactions, minimum_support)
    # generate frequent item sets
    frequent_set = list()
    n = 2
    k = len(candidate_set)
    while n <= k:
        candidate_set = self_join(candidate_set, n)
        if len(candidate_set) == 0: break
        candidate_set = [e for e in candidate_set if minimum_support_is_satisfied(e, d, number_of_transactions, minimum_support)]
        for e in candidate_set: e.sort()
        candidate_set.sort()
        frequent_set.extend(candidate_set)
        n = n + 1 
    # generate association rules
    candidate_association_rules = generate_association_rules(frequent_set)
    result = [r for r in candidate_association_rules if minimum_confidence_is_satisfied(r, d, number_of_transactions, minimum_confidence)]
    return result

def brute_force(minimum_support, minimum_confidence, transaction_database_id):
    d = get_transactions(transaction_database_id)
    if d is None or len(d) == 0: return None
    number_of_transactions = len(d)
    items = get_items(d)
    # generate frequent item sets
    frequent_set = list()
    n = 2
    k = len(items)
    while n <= k:
        #candidate_set = list(combinations(items, n))
        candidate_set = [e for e in combinations(items, n) if minimum_support_is_satisfied(e, d, number_of_transactions, minimum_support)]
        if len(candidate_set) == 0: break
        for e in candidate_set: e.sort()
        candidate_set.sort()
        frequent_set.extend(candidate_set)
        n = n + 1
    # generate association rules
    candidate_association_rules = generate_association_rules(frequent_set)
    result = [r for r in candidate_association_rules if minimum_confidence_is_satisfied(r, d, number_of_transactions, minimum_confidence)]
    return result
    
def main():
    #minimum_support = raw_input("Enter minimum support: ")
    #minimum_confidence = raw_input("Enter minimum confidence: ")
    minimum_support = 0.15
    minimum_confidence = 0.50
    print("Minimum support", minimum_support)
    print("Minimum confidence", minimum_confidence)
    for db in range(1, 6):
    
        start_time = time.time()
        print("Processing Apriori algorithm for database", db)
        a_rules = apriori(float(minimum_support), float(minimum_confidence), db)
        print("Number of association rules generated by Apriori algorithm", len(a_rules))
        print("--- %s seconds elapsed ---" % (time.time() - start_time))
        print("Rules generated by Apriori algorithm:")
        for rule in a_rules:
            print(rule)
        
        start_time = time.time()
        print("Processing brute force algorithm for database", db)
        b_rules = brute_force(float(minimum_support), float(minimum_confidence), db)
        print("Number of association rules generated by brute force algorithm", len(b_rules))
        print("--- %s seconds elapsed ---" % (time.time() - start_time))
        print("Rules generated by brute force algorithm:")
        for rule in b_rules:
            print(rule)

if __name__ == "__main__":
    main()