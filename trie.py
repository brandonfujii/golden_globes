# trie.py
# Class for trie data structure.

class Trie(object):
	def __init__(self, items=None, values=None):
		self.children = defaultdict(Trie)
		self.value = None
		if items and values:
			for item, value in zip(items, values):
				self.insert(item, value)
		elif items:
			for item in items:
				self.insert(item)

	def __getitem__(self, item):
		if len(item) == 0:
			return self
		elif item[0] in self.children:
			return self.children[item[0]][item[1:]]
		else:
			return None

	def __setitem__(self, item, value):
		self.insert(item, value)

	def __contains__(self, item):
		return bool(self[item])

	def __delitem__(self, item):
		if len(item) == 0:
			self.children[item[0]].value = None
		else:
			del self.children[item[0]][item[1:]]
			if len(self.children[item[0]].children) == 0:
				del self.children[item[0]]

	def __str__(self):
		return 'Trie(%s, %s children)' % (self.value, len(self.children))

	def insert(self, item, value=None):
		value = value if value is not None else item
		if len(item) == 0:
			self.value = value
		else:
			self.children[item[0]].insert(item[1:], value)

	def walk(self, fn, direction='down', prefix=None):
		"""
		Walk the trie and call fn on it and each of its subtries.

		fn should take three arguments:
		    trie  - the trie itself
		    key   - the key of the trie relative to its root
		    value - the trie's value

		direction can be 'down' (default) or 'up'.  'down'
		ensures that fn is called on a trie before any of that
		trie's children.  'up' ensures that fn is called on all
		of a trie's children before being called on the trie itself.
		"""
		if direction != 'down' and direction != 'up':
			raise ValueError('direction must be "up" or "down"!')
		prefix = prefix if prefix is not None else tuple()
		if direction == 'down':
			fn(self, prefix, self.value)
		for key in self.children:
			child = self.children[key]
			child.walk(fn, direction, prefix + (key,))
		if direction == 'up':
			fn(self, prefix, self.value)
