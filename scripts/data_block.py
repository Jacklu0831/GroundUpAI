# ---------------------------------------------
# | THIS FILE WAS AUTOGENERATED! DO NOT EDIT! |
# ---------------------------------------------
# edit notebooks/02_data_block.ipynb and run generate_all.py

import sys
sys.path.insert(0, '/'.join(sys.path[0].split('/')[:-1] + ['scripts']))

from typing import *
import PIL
import mimetypes
from functools import partial
from pathlib import Path
from parameter import *

Path.ls = lambda x: list(x.iterdir())

image_exts = set(k for k,v in mimetypes.types_map.items() if v.startswith('image/'))
' '.join(image_exts)

from collections import OrderedDict

def listify(inp):
    if inp is None: return []
    if isinstance(inp, list): return inp
    if isinstance(inp, str): return [inp]
    if isinstance(inp, Iterable): return list(inp)
    return [inp]

def setify(inp):
    return inp if isinstance(inp, set) else set(listify(inp))

def uniqueify(items, sort=False):
    res = list(OrderedDict.fromkeys(items).keys())
    return res.sort() if sort else res

def get_files(path, exts=None, recurse=False, include=None):
    def get_file_paths(path, files, exts=None):
        # filenames -> PosixPaths filtered by extensions
        path = Path(path)
        in_exts = lambda o: (not exts) or (f".{o.split('.')[-1].lower()}" in exts)
        return [path/f for f in files if not is_hidden(f) and in_exts(f)]

    path, exts = Path(path), {e.lower() for e in setify(exts)}
    is_hidden = lambda o: o.startswith('.')

    if recurse:
        files = []
        for i, (p, d, f) in enumerate(os.walk(path)):
            if include and i == 0:
                d[:] = [o for o in d if o in include]
            else:
                d[:] = [o for o in d if not is_hidden(o)]
            files += get_file_paths(p, f, exts)
    else:
        filenames = [o.name for o in os.scandir(path) if o.is_file()]
        files = get_file_paths(path, filenames, exts)
    return files

class ListContainer():
    def __init__(self, items): self.items = listify(items)

    def __getitem__(self, idx):
        if isinstance(idx, torch.Tensor):
            idx = int(idx.item())
        if isinstance(idx, (int, slice)):
            return self.items[idx]
        if isinstance(idx[0], bool):
            assert len(idx) == len(self)
            return [o for m, o in zip(idx, self.items) if m]
        return [self.items[i] for i in idx]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __setitem__(self, i, o):
        self.items[i] = o

    def __delitem__(self, i):
        del(self.items[i])

    def __repr__(self):
        res = f'{self.__class__.__name__} ({len(self)} items)\n{self.items[:10]}'
        if len(self) > 10:
            return res[:-1]+ ' ...]'
        return res

def compose(item, fns, *args, order_key='_order', **kwargs):
    key = lambda o: getattr(o, order_key, 0)
    for fn in sorted(listify(fns), key=key):
        item = fn(item, **kwargs)
    return item

class ItemList(ListContainer):
    def __init__(self, items, path='.', transforms=None):
        super().__init__(items)
        self.path = Path(path)
        self.transforms = transforms

    def new(self, items, cls=None):
        # used for train/valid split
        cls = cls if cls else self.__class__
        return cls(items, self.path, self.transforms)

    def get(self, i): # subclassed for method of accessing
        return i

    def _get(self, i): # apply additional transforms
        return compose(self.get(i), self.transforms)

    def __getitem__(self, i):
        items = super().__getitem__(i)
        if isinstance(items, list):
            return [self._get(o) for o in items]
        return self._get(items)

    def __repr__(self):
        return f'Path: {self.path}\n{super().__repr__()}'

class ImageList(ItemList):
    @classmethod
    def from_files(cls, path, exts=image_exts, recurse=True, include=None, **kwargs):
        files = get_files(path, exts, recurse, include)
        return cls(files, path, **kwargs)

    def get(self, fn): # override parent fn
        return PIL.Image.open(fn)

class Transform():
    _order = 0

class ResizeFixed(Transform):
    _order = 10
    def __init__(self, size):
        self.size = (size, size) if isinstance(size, int) else size

    def __call__(self, item):
        return item.resize(self.size, PIL.Image.BILINEAR)

def to_black_white(item):
    return item

def to_byte_tensor(item):
    w, h = item.size
    byte_tensor = torch.ByteTensor(torch.ByteStorage.from_buffer(item.tobytes()))
    # channel first
    return byte_tensor.view(h, w, -1).permute(2, 0, 1)

def to_float_tensor(item):
    return item.float().div_(255.)

def make_rgb(item):
    return item.convert('RGB')

make_rgb._order = 0
to_byte_tensor._order = 20
to_float_tensor._order = 30

def split_grandparent(filepath, train_name='train', valid_name='valid'):
    ret = {valid_name: False, train_name: True}
    return ret.get(filepath.parent.parent.name, None)

def split_by_fn(item_list, fn):
    mask = [fn(o) for o in item_list]
    true  = [o for o, m in zip(item_list, mask) if m == True]
    false = [o for o, m in zip(item_list, mask) if m == False]
    return true, false

class SplitData():
    def __init__(self, train, valid):
        self.train = train
        self.valid = valid

    def __getattr__(self, k):
        # delegate getattr
        return getattr(self.train, k)

    def __setstate__(self, data: Any):
        # for pickling
        self.__dict__.update(data)

    @classmethod
    def split_by_fn(cls, item_list, fn):
        splitted = split_by_fn(item_list, fn)
        lists = map(lambda items: item_list.new(items), splitted)
        return cls(*lists)

    def __repr__(self):
        return f'{self.__class__.__name__}\n\nTRAIN:\n{self.train}\n\nVALID:\n{self.valid}\n'

class Processor():
    def process(self, items):
        return items

class CategoryProcessor(Processor):
    def __init__(self):
        self.vocab = None

    # process/deprocess 1 item
    def proc(self, item):
        return self.o2i[item]
    def deproc(self, label):
        return self.vocab[label]

    def __call__(self, items):
        if not self.vocab:
            self.vocab = uniqueify(items)
            self.o2i = {v: k for k, v in enumerate(self.vocab)}
        return [self.proc(o) for o in items]

    def deprocess(self, idxs):
        assert self.vocab, 'uninitialized vocab in CategoryProcessor'
        return [self.deproc(i) for i in idxs]

def p_name(filepath):
    return filepath.parent.name

def gp_name(filepath):
    return filepath.parent.parent.name

class LabeledData():
    def __init__(self, x, y, proc_x, proc_y):
        self.x = self.process(x, proc_x)
        self.y = self.process(y, proc_y)
        self.proc_x = proc_x
        self.proc_y = proc_y

    def __getitem__(self, i):
        return self.x[i], self.y[i]

    def __len__(self):
        return len(self.x)

    def __repr__(self):
        return f'{self.__class__.__name__}\nx data: {self.x}\ny data: {self.y}\n'

    def process(self, item_list, proc):
        return item_list.new(compose(item_list.items, proc))

    def obj(self, items, i, procs):
        isint = isinstance(i, int) or isinstance(i, torch.LongTensor) and not i.ndim
        item = items[i]
        for proc in reversed(listify(procs)):
            item = proc.deproc(item) if isint else proc.deprocess(item)
        return item

    def x_obj(self, i):
        return self.obj(self.x, i, self.proc_x)

    def y_obj(self, i):
        return self.obj(self.y, i, self.proc_y)

    @classmethod
    def label_by_fn(cls, item_list, fn, proc_x=None, proc_y=None):
        labels = [fn(o) for o in item_list.items]
        labels = ItemList(labels, path=item_list.path)
        return cls(item_list, labels, proc_x, proc_y)

def label_by_fn(splitted_data, fn, proc_x=None, proc_y=None):
    train = LabeledData.label_by_fn(splitted_data.train, fn, proc_x, proc_y)
    valid = LabeledData.label_by_fn(splitted_data.valid, fn, proc_x, proc_y)
    return SplitData(train, valid)

def show_image(img, figsize=(3, 3)):
    plt.figure(figsize=figsize)
    plt.axis('off')
    plt.imshow(img.permute(1, 2, 0))