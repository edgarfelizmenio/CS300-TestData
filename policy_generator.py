import json
import random
import os

attr_file = open('attributes.json', 'r')
attributes = json.load(attr_file)

operations = ["and", "or"]
num_attributes = 40
key_size = num_attributes/2
num_runs = 10
num_users = 20

class TreeNode(object):
    def __init__(self):
        self.lson = None
        self.rson = None
        self.value = None

def generate_random_policy(num_attributes, key_size, attributes):
    random.shuffle(attributes)
    root = generate_tree(num_attributes)
    assign_values(root, attributes[:num_attributes])
    policy = get_policy_string(root)
    keys = get_satisfying_attributes(root, key_size)
    return policy, keys

def generate_tree(num_attributes):
    root = None
    n = 0
    while n < num_attributes:
        if root is None:
            root = TreeNode()
        else:
            alpha = root
            while alpha.lson is not None or alpha.rson is not None:
                choice = random.randint(0,1)
                if choice == 0:
                    alpha = alpha.lson
                else:
                    alpha = alpha.rson
            alpha.lson = TreeNode()
            alpha.rson = TreeNode()
        n += 1
    return root

def assign_values(root, attributes):
    if not (root.lson is None and root.rson is None):
        root.value = random.choice(operations)
        assign_values(root.lson, attributes)
        assign_values(root.rson, attributes)
    else:
        root.value = attributes.pop()


def get_policy_string(root):
    if not (root.lson is None and root.rson is None):
        return '({} {} {})'.format(get_policy_string(root.lson), root.value, get_policy_string(root.rson))
    else:
        return '{}'.format(root.value)

def get_satisfying_attributes(root, key_size):
    if not (root.lson is None and root.rson is None):
        left_attributes = get_satisfying_attributes(root.lson, key_size)
        right_attributes = get_satisfying_attributes(root.rson, key_size)
        if root.value == "or":
            return random.choice([left_attributes, right_attributes])
        else:
            return left_attributes + right_attributes
    else:
        return [root.value]


# policy, keys = generate_random_policy(num_attributes, key_size, attributes)
# print(policy)
# keys = list(filter(lambda y: len(y) == key_size, keys))
# for key in keys:
#     random.shuffle(key)
#     print(key)


if not os.path.exists('policies'):
    os.mkdir('policies')

policy_sizes = [8, 16, 32, 64]
key_sizes = [4, 8, 16, 32, 64]

for policy_size in policy_sizes:
    size_dir = os.path.join('policies','length_{}'.format(policy_size))
    if not os.path.exists(size_dir):
        os.mkdir(size_dir)

    for key_size in key_sizes:
        key_dir = os.path.join(size_dir, '{} attributes in key'.format(key_size))
        if not os.path.exists(key_dir):
            os.mkdir(key_dir)

        for i in range(num_runs):
            users = []
            for j in range(num_users):
                while True:
                    policy, key = generate_random_policy(policy_size, key_size, attributes)
                    if len(key) <= key_size:
                        missing = key_size - len(key)
                        
                        while missing > 0:
                            attribute = random.choice(attributes)
                            if attribute not in key:
                                key.append(attribute)
                                missing -= 1
                        break
                users.append({
                    'policy': policy,
                    'key': key
                })

            run_file = open(os.path.join(key_dir, 'run {}.json'.format(i)), "w")
            json.dump(users, run_file)
            run_file.close()
            print(run_file.name)

    