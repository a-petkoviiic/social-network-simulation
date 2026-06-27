class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        curr_node = self.root
        for char in word:
            if char not in curr_node.children:
                curr_node.children[char] = TrieNode()
            curr_node = curr_node.children[char]
        curr_node.is_end_of_word = True

    def collect_words(self, node, prefix):
        results = []
        if node.is_end_of_word:
            results.append(prefix)
        for char, child in node.children.items():
            results.extend(self.collect_words(child, prefix + char))
        return results

    def autocomplete(self, prefix):
        curr_node = self.root
        for char in prefix:
            if char not in curr_node.children:
                return []
            curr_node = curr_node.children[char]
        return self.collect_words(curr_node, prefix)



