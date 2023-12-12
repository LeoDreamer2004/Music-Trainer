# 2023秋音乐与数学期中大作业

## 作业要求

本次作业要求利用 **遗传算法(Genetic Algorithm)** 来进行机器作曲。通过随机生成或根据现有音乐片段，建立合适的适应度函数(fitness function)指引进化，生成更好的音乐片段。

---

## 实验工具

midi文件能更好地建立起音乐与计算机之间的联系。在Python语言中，对midi文件有较好的第三方模块支持，以下代码基于其中使用最多的`mido`库进行。

为此，在文件目录下打开命令行中执行

```shell
pip install -r requirements.txt
```

来安装必要的依赖。

所有的midi文件均存放于`midi`文件夹下。为了能更方便地预览midi，使用musescore4进行midi的展示。

---

## 算法设计

遗传算法模拟自然界的自然选择定律，对一个族群进行繁衍迭代，在遗传的过程中可能发生变异(mutate)、交叉(crossover)的行为，要求我们建立一个合适的适应度(fitness)函数对子代进行筛选，最终趋于适应环境。

为了便于算法的设计，我们采用先训练好节奏，随后再对于固定的节奏来生成音调进行训练。因此训练分离为 **节奏(ryhthm)** 和 **音调(pitch)** 两部分。

### 节奏部分

#### 交叉

我们采用这样的交叉方式：对于音轨A和音轨B，随机选取一个索引i,把A音轨的i小节之前与B音轨的第i小节之后直接进行拼接。特别地出于适应度的考虑我们规定这个索引i是偶数。

#### 变异

我们为节奏设计了四种变异算法：

- 交换两个音符的时值
- 把一个音符分成两个音符
- 把两个音符合并为一个音符
- 把一个小节的全部音符复制到另一个小节

#### 适应度

衡量适应度有多方面的因素，包括：

- 我们希望强拍上有音，例如对于一个4/4拍曲子，一个小节当中的第一拍和第三拍最好有音。
![节奏实例1](img/ryhthm1.png)
在这个例子当中，第一小节的一三拍都有音，而第二小节则不然，因此我们给第二小节一个负权重。
适应度公式：
$$f_1 = r_1(b-2n)$$
这里$r_1$是权重系数，$b$是强拍音数量，$n$是小节数。

- 如果一个曲子的节奏存在呼应，那么是很好的。特别地，对于一个8小节的曲子，我们希望1,3; 2,4; 4,6; 5,7小节是呼应的。可以简单建立搞一个描述两小节相似度的函数。
适应度公式：
$$f_2 = \sum c_{i,j}=\sum \frac{\left| I\cap J\right|}{}$$

---

## 代码实现

### 模块包装

`mido`原本的逻辑是把midi文件剖分为若干音轨，每个音轨是一个列表，内部按照 **事件** 逻辑来存储音符信息。例如元事件：

```py
mido.MetaMessage("key_signature", key="C", time=0)
```

用于签订调式为C大调，而事件

```py
mido.Message("note_on", note=72, velocity=80, time=480)
```

用于声明一个音符发出的事件，距离上一个事件结束480tick(=1拍)。该音符为C5(=72)，音量为80。

由于以下的作曲非常简单，没有必要使用`mido`中这样复杂的功能，因此我们对`mido`库做出了包装，即`midoWrapper`。其中提供了对音符的类`Note`包装和音轨的类`Track`包装。以下介绍运行逻辑和一些重要的函数。

```py
class Note:
    def __init__(
        self, pitch: Pitch_T, length: int, start_time: int, velocity: int = VELOCITY
    ):
        # Here the "time" is "tick" in mido actually
        self.pitch = pitch
        self.length = length
        self.start_time = start_time
        self.velocity = velocity
    
    @property
    def end_time(self):
        return self.start_time + self.length
```

类`Note`中的音符包含音高、长度、起始时间（指在音轨中的绝对时间，而非原本`mido`库中与上一事件的相对时间）和音量信息，同时提供查询结束时间的属性。此外，也提供了音名（例如C5）与midi音高编码（例如72）之间的转化接口，判断一个音是否在一个固定的调式中等等。

特别地，我们提供了一个随机生成指定调式音符的接口：

```py
def random_pitch_in_mode(
    key: Key_T, min_pitch: int = NOTE_MIN, max_pitch: int = NOTE_MAX
): ...
```

其中`Key_T`类型同时兼容大调和小调的调式名称（例如`C#`或`Ebm`）而`min_pitch`和`max_pitch`标定了生成音符的范围。

```py
class Track:
    def __init__(self, instrument: int = 0, key: Key_T = "C"):
        self.instrument = instrument
        self.key = key
        self.note: List[Note] = []
```

类`Track`当中重点强调了乐器和调式的属性，同时把所有的音符置于一个列表当中。

其中提供了与`mido`内置的`midiTrack`类型的相互转化接口：

```py
def from_track(track: mido.MidiTrack) -> "Track": ...
def to_track(self) -> mido.MidiTrack: ...
```

同时，由于我们的节奏训练和音调训练是分离进行的，因此我们给出了两个函数，分别用于生成随机音轨和在给定节奏之上生成随机的音高：

```py
def generate_random_track(self, bar_number: int): ...
def generate_random_pitch_on_rhythm(self, track: "Track"): ...
```

尤其要强调的是，我们也实现了 **移调、倒影和逆行** 的三个变换：

```py
def transpose(self, interval): ...
def inverse(self, center): ...
def retrograde(self): ...
```

最后，我们也提供了一些简单的函数，分别用于进行midi文件的生成、解析、存储。

```py
def generate_midi(key: Key_T = None): ...
def parse_midi(filename: str): ...
def save_midi(s: mido.MidiFile, filename: str): ...
```

### 音轨的生成与读取

具体内容详见 [测试代码](wrapperTest.py) 。

- 在`generate_random_midi_test`中，我们建立了一个空白的midi文件，并利用`generate_random_track`生成了一个#g小调的4小节随机音乐片段。随后将音轨进行深拷贝，再对其作逆行变换，作为第二条音轨添加进去。这样，输出了一个双音轨的音乐片段，其中两个音轨互为逆行关系。
![随机片段](img/random_piece.png)

- 在`read_midi_test`中，我们对一个现有的midi文件进行解析，并打印出基本信息。这段midi节选自久石让的《Summer》。可以对`Track`类型直接调用`print`函数来输出内部音符的具体信息。
![测试midi](img/test_midi.png)

    ```txt
    Key: D
    Instrument: 0
    Length: 15353
    Bar: 8
    ----------------
    Key: D
    Instrument: 0
    Length: 15347
    Bar: 8
    ```
