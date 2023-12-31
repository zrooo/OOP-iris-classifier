import abc
import math
import random
import datetime
import collections
import collections.abc
from typing import (
    Optional, Iterable, Union, Counter, 
    TypedDict, List, overload, Tuple
)

from src.model import Sample


class Sample:
    """Abstract superclass for all samples."""

    def __init__(
        self,
        sepal_length: float,
        sepal_width: float,
        petal_length: float,
        petal_width: float,
    ) -> None:
        self.sepal_length = sepal_length
        self.sepal_width = sepal_width
        self.petal_length = petal_length
        self.petal_width = petal_width

    def __eq__(self, other: Any) -> bool:
        if type(other) != type(self):
            return False
        other = cast(Sample, other)
        return all(
            [
                self.sepal_length == other.sepal_length,
                self.sepal_width == other.sepal_width,
                self.petal_length == other.petal_length,
                self.petal_width == other.petal_width,
            ]
        )

    @property
    def attr_dict(self) -> dict[str, str]:
        return dict(
            sepal_length=f"{self.sepal_length!r}",
            sepal_width=f"{self.sepal_width!r}",
            petal_length=f"{self.petal_length!r}",
            petal_width=f"{self.petal_width!r}",
        )

    def __repr__(self) -> str:
        base_attributes = self.attr_dict
        attrs = ", ".join(f"{k}={v}" for k, v in base_attributes.items())
        return f"{self.__class__.__name__}({attrs})"


class Purpose(enum.IntEnum):
    Classification = 0
    Testing = 1
    Training = 2


class KnownSample(Sample):
    """Represents a sample of testing or training data, the species is set once
    The purpose determines if it can or cannot be classified.
    """

    def __init__(
        self,
        sepal_length: float,
        sepal_width: float,
        petal_length: float,
        petal_width: float,
        purpose: int,
        species: str,
    ) -> None:
        purpose_enum = Purpose(purpose)
        if purpose_enum not in {Purpose.Training, Purpose.Testing}:
            raise ValueError(f"Invalid purpose: {purpose!r}: {purpose_enum}")
        super().__init__(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
        )
        self.purpose = purpose_enum
        self.species = species
        self._classification: Optional[str] = None

    def matches(self) -> bool:
        return self.species == self.classification

    @property
    def classification(self) -> Optional[str]:
        if self.purpose == Purpose.Testing:
            return self._classification
        else:
            raise AttributeError(f"Training samples have no classification")



    @classification.setter
    def classification(self, value: str) -> None:
        if self.purpose == Purpose.Testing:
            self._classification = value
        else:
            raise AttributeError(f"Training samples cannot be classified")

    def __repr__(self) -> str:
        base_attributes = self.attr_dict
        base_attributes["purpose"] = f"{self.purpose.value}"
        base_attributes["species"] = f"{self.species!r}"
        if self.purpose == Purpose.Testing and self._classification:
            base_attributes["classification"] = f"{self._classification!r}"
        attrs = ", ".join(f"{k}={v}" for k, v in base_attributes.items())
        return f"{self.__class__.__name__}({attrs})"


class UnknownSample(Sample):
    """A sample provided by a User, to be classified."""

    def __init__(
        self,
        sepal_length: float,
        sepal_width: float,
        petal_length: float,
        petal_width: float,
    ) -> None:
        super().__init__(
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
        )
        self._classification: Optional[str] = None

    @property
    def classification(self) -> Optional[str]:
        return self._classification

    @classification.setter
    def classification(self, value: str) -> None:
        self._classification = value

    def __repr__(self) -> str:
        base_attributes = self.attr_dict
        base_attributes["classification"] = f"{self.classification!r}"
        attrs = ", ".join(f"{k}={v}" for k, v in base_attributes.items())
        return f"{self.__class__.__name__}({attrs})"


class Distance:
    """A distance computation"""

    def distance(self, s1: Sample, s2: Sample) -> float:
        raise NotImplementedError


class Chebyshev(Distance):
    """
    Computes the Chebyshev distance between two samples.

    ::

        >>> from math import isclose
        >>> from model import KnownSample, Purpose, UnknownSample, Chebyshev

        >>> s1 = KnownSample(
        ...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa",
        ...     purpose=Purpose.Training)
        >>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

        >>> algorithm = Chebyshev()
        >>> isclose(3.3, algorithm.distance(s1, u))
        True

    """

    def distance(self, s1: Sample, s2: Sample) -> float:
        return max(
            [
                abs(s1.sepal_length - s2.sepal_length),
                abs(s1.sepal_width - s2.sepal_width),
                abs(s1.petal_length - s2.petal_length),
                abs(s1.petal_width - s2.petal_width),
            ]
        )


class Minkowski(Distance):
    """An abstraction to provide a way to implement Manhattan and Euclidean."""

    m: int

    def distance(self, s1: Sample, s2: Sample) -> float:
        return (
            sum(
                [
                    abs(s1.sepal_length - s2.sepal_length) ** self.m,
                    abs(s1.sepal_width - s2.sepal_width) ** self.m,
                    abs(s1.petal_length - s2.petal_length) ** self.m,
                    abs(s1.petal_width - s2.petal_width) ** self.m,
                ]
            )
            ** (1 / self.m)
        )


class Euclidean(Minkowski):
    m = 2


class Manhattan(Minkowski):
    m = 1


class Sorensen(Distance):
    def distance(self, s1: Sample, s2: Sample) -> float:
        return sum(
            [
                abs(s1.sepal_length - s2.sepal_length),
                abs(s1.sepal_width - s2.sepal_width),
                abs(s1.petal_length - s2.petal_length),
                abs(s1.petal_width - s2.petal_width),
            ]
        ) / sum(
            [
                s1.sepal_length + s2.sepal_length,
                s1.sepal_width + s2.sepal_width,
                s1.petal_length + s2.petal_length,
                s1.petal_width + s2.petal_width,
            ]
        )


class Reduce_Function(Protocol):
    """Define a callable object with specific parameters."""

    def __call__(self, values: list[float]) -> float:
        pass


class Minkowski_2(Distance):
    """A generic way to implement Manhattan, Euclidean, and Chebyshev.

    ::

        >>> from math import isclose
        >>> from model import KnownSample, Purpose, UnknownSample, Minkowski_2


        >>> class CD(Minkowski_2):
        ...     m = 1
        ...     reduction = max

        >>> s1 = KnownSample(
        ...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa",
        ...     purpose=Purpose.Training)
        >>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

        >>> algorithm = CD()
        >>> isclose(3.3, algorithm.distance(s1, u))
        True

    """

    m: int
    reduction: Reduce_Function

    def distance(self, s1: Sample, s2: Sample) -> float:
        # Required to prevent Python from passing `self` as the first argument.
        summarize = self.reduction
        return (
            summarize(
                [
                    abs(s1.sepal_length - s2.sepal_length) ** self.m,
                    abs(s1.sepal_width - s2.sepal_width) ** self.m,
                    abs(s1.petal_length - s2.petal_length) ** self.m,
                    abs(s1.petal_width - s2.petal_width) ** self.m,
                ]
            )
            ** (1 / self.m)
        )


class Hyperparameter:
    """A hyperparameter value and the overall quality of the classification."""

    def __init__(self, k: int, algorithm: "Distance", training: "TrainingData") -> None:
        self.k = k
        self.algorithm = algorithm
        self.data: weakref.ReferenceType["TrainingData"] = weakref.ref(training)
        self.quality: float

    def test(self) -> None:
        """Run the entire test suite."""
        training_data: Optional["TrainingData"] = self.data()
        if not training_data:
            raise RuntimeError("Broken Weak Reference")
        pass_count, fail_count = 0, 0
        for sample in training_data.testing:
            sample.classification = self.classify(sample)
            if sample.matches():
                pass_count += 1
            else:
                fail_count += 1
        self.quality = pass_count / (pass_count + fail_count)

    def classify(self, sample: Sample) -> str:
        """The k-NN algorithm"""
        training_data = self.data()
        if not training_data:
            raise RuntimeError("No TrainingData object")
        distances: list[tuple[float, KnownSample]] = sorted(
            (self.algorithm.distance(sample, known), known)
            for known in training_data.training
        )
        k_nearest = (known.species for d, known in distances[: self.k])
        frequency: Counter[str] = collections.Counter(k_nearest)
        best_fit, *others = frequency.most_common()
        species, votes = best_fit
        return species


class TrainingData:
    """A set of training data and testing data with methods to load and test the samples."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.uploaded: datetime.datetime
        self.tested: datetime.datetime
        self.training: list[KnownSample] = []
        self.testing: list[KnownSample] = []
        self.tuning: list[Hyperparameter] = []

    def load(self, raw_data_iter: Iterable[dict[str, str]]) -> None:
        """Extract TestingKnownSample and TrainingKnownSample from raw data"""
        for n, row in enumerate(raw_data_iter):
            purpose = Purpose.Testing if n % 5 == 0 else Purpose.Training
            sample = KnownSample(
                sepal_length=float(row["sepal_length"]),
                sepal_width=float(row["sepal_width"]),
                petal_length=float(row["petal_length"]),
                petal_width=float(row["petal_width"]),
                purpose=purpose,
                species=row["species"],
            )
            if sample.purpose == Purpose.Testing:
                self.testing.append(sample)
            else:
                self.training.append(sample)
        self.uploaded = datetime.datetime.now(tz=datetime.timezone.utc)

    def test(self, parameter: Hyperparameter) -> None:
        """Test this hyperparamater value."""
        parameter.test()
        self.tuning.append(parameter)
        self.tested = datetime.datetime.now(tz=datetime.timezone.utc)

    def classify(self, parameter: Hyperparameter, sample: UnknownSample) -> str:
        return parameter.classify(sample)
    
class TrainingKnownSample():
    ...

class BadSampleRow(ValueError):
    pass


class SampleReader:
    """See iris.names for attribute ordering in bezdekIris.data file"""

    target_class = Sample
    header = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]

    def __init__(self, source: Path) -> None:
        self.source = source

    def sample_iter(self) -> Iterator[Sample]:
        target_class = self.target_class
        with self.source.open() as source_file:
            reader = csv.DictReader(source_file, self.header)
            for row in reader:
                try:
                    sample = target_class(
                        sepal_length=float(row["sepal_length"]),
                        sepal_width=float(row["sepal_width"]),
                        petal_length=float(row["petal_length"]),
                        petal_width=float(row["petal_width"]),
                    )
                except ValueError as ex:
                    raise BadSampleRow(f"Invalid {row!r}") from ex
                yield sample

class TestingKnownSample():
    ...
    

class SampleDict(TypedDict):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    species: str

class SamplePartition(List[SampleDict], abc.ABC): #추상클래스로 선언/ 리스트를 상속받음
    @overload
    def __init__(self, *, training_subsset: float = 0.80) -> None:   # *은 파티션 역할
        ...

    @overload
    def __init__(
            self, 
            iterable: Optional[Iterable[SampleDict]] = None,
            *,
            training_subset: float = 0.80
    )-> None:
            ...

    def __init__(
            self, 
            iterable: Optional[Iterable[SampleDict]] = None,
            *,
            training_subset: float = 0.80
    ) -> None:
        self.training_subset = training_subset
        if iterable:
                super().__init__(iterable)
        else:
                super().__init__()
#overloading 왜 같은 걸 여러개 만드는가->데이터타입마다작동이달라짐

    @abc.abstractproperty
    @property
    def training(self) -> list[TrainingKnownSample]:
            ...
            
    @abc.abstractproperty           
    @property
    def testing(self) -> list[TestingKnownSample]:
            ...
#추상 클래스 다른 개발자들이 사용할 때 지켜야 하는 최소한의 틀? 구현을 해놓진 않는다~

class ShufflingSamplePartition(SamplePartition):  #샘플파티션을 상속받음 올라가보면 샘플파티션은 리스트를 상속받았으므로?
#데이터의 인덱스를 셔플링. 항상 새롭게 순서를 바꿔 주는 클래스
    def __init__(
        self,
        iterable: Optional[Iterable[SampleDict]] = None,
        *,
        training_subset: float = 0.80  #부분집합은 80퍼센트만 가져갈게
    ) -> None:
        super().__init__(iterable, training_subset)
        self.split: Optional[int] = None

    @property
    def training(self) -> list[TrainingKnownSample]:
        self.shuffle()
        return [TrainingKnownSample(**sd) for sd in self[:self.split]]  #**sd: unpack
 
    @property  
    def testing(self) -> list[TestingKnownSample]:
        ...

    def shuffle(self) -> None:
        if not self.split:
            random.shuffle(self)
            self.split = int(len(self) * self.training_subset)  #int는 천장함수 아니고 바닥함수

class DealingPartition(abc.ABC):
    def __init__(
        self, 
        items: Optional[Iterable[SampleDict]],
        #/, 왼쪽, 파이썬의 파티션 구현은 두 가지argument냐 keywordargument냐에 따라 다르게 파티션 구분
        *, #오른쪽
        training_subset: Tuple[int, int] = (8, 10)
    ) -> None:
        ...

    @abc.abstractproperty
    @property
    def training(self) -> List[TrainingKnownSample]:
        ...

    @abc.abstractproperty
    @property
    def testing(self) -> List[TestingKnownSample]:
        ...

    @abc.abstractmethod
    def extend(self, items: Iterable[SampleDict]) -> None:
        ...

    @abc.abstractmethod
    def append(self, item: SampleDict) -> None:
        ...
#extend append 차이: 하나와 여러개 입력

class CountingDealingPartition(DealingPartition):
    def __init__(   
            self,
            items: Iterable[SampleDict], 
            *,
            traing_subset: Tuple[int, int] = (8, 10)
    ) -> None:
        self.traing_subset = training_subset
        self.counter = 0
        self._training: list[TrainingKnownSample] = []
        self._testing: list[TestingKnownSample] = [] #파이썬 앞에서 언더바가 붙으면 이 객체 안에서만 사용되는 특성
        if items:
            self.extend(items)

    def extend(self, items: Iterable[SampleDict]) -> None:
        for item in items:
            self.append(item)

    def append(self, item: SampleDict) -> None:
        n, d = self.training_subset
        if self.counter % d < n:
            self._training.append(TrainingKnownSample(**item))
        else:
            self._testing.append(TestingKnownSample(**item)) #언팩
        self.counter += 1

    @property
    def training(self) -> list[TrainingKnownSample]:
        return self._training
    
    @property
    def testing(self) -> list[TestingKnownSample]:
        return self._testing

    

# Special case, we don't *often* test abstract superclasses.
# In this example, however, we can create instances of the abstract class.
test_Sample = """
>>> x = Sample(1, 2, 3, 4)
>>> x
Sample(sepal_length=1, sepal_width=2, petal_length=3, petal_width=4)
"""

test_Training_KnownSample = """
>>> s1 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Training.value)
>>> s1
KnownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, purpose=2, species='Iris-setosa')
>>> s1.classification
Traceback (most recent call last):
...
AttributeError: Training samples have no classification
>>> s1.classification("rejected")
Traceback (most recent call last):
...
AttributeError: Training samples have no classification
"""

test_Testing_KnownSample = """
>>> s2 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Testing.value)
>>> s2
KnownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, purpose=1, species='Iris-setosa')
>>> s2.classification
>>> s2.classification = "wrong"
>>> s2
KnownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, purpose=1, species='Iris-setosa', classification='wrong')
"""

test_UnknownSample = """
>>> u = UnknownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, )
>>> u
UnknownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, classification=None)
>>> u.classification = "something"
>>> u
UnknownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, classification='something')
"""

test_Chebyshev = """
>>> s1 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Training.value)
>>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

>>> algorithm = Chebyshev()
>>> isclose(3.3, algorithm.distance(s1, u))
True
"""

test_Euclidean = """
>>> s1 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Training.value)
>>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

>>> algorithm = Euclidean()
>>> isclose(4.50111097, algorithm.distance(s1, u))
True
"""

test_Manhattan = """
>>> s1 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Training.value)
>>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

>>> algorithm = Manhattan()
>>> isclose(7.6, algorithm.distance(s1, u))
True
"""

test_Sorensen = """
>>> s1 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Training.value)
>>> u = UnknownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4})

>>> algorithm = Sorensen()
>>> isclose(0.2773722627, algorithm.distance(s1, u))
True
"""

test_Hyperparameter = """
>>> td = TrainingData('test')
>>> s2 = KnownSample(
...     sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species="Iris-setosa", purpose=Purpose.Testing.value)
>>> td.testing = [s2]
>>> t1 = KnownSample(**{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2, "species": "Iris-setosa", "purpose": 1})
>>> t2 = KnownSample(**{"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4, "species": "Iris-versicolor", "purpose": 1})
>>> td.training = [t1, t2]
>>> h = Hyperparameter(k=3, algorithm=Chebyshev(), training=td)
>>> u = UnknownSample(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2)
>>> h.classify(u)
'Iris-setosa'
>>> h.test()
>>> print(f"data={td.name!r}, k={h.k}, quality={h.quality}")
data='test', k=3, quality=1.0
"""

test_TrainingData = """
>>> td = TrainingData('test')
>>> raw_data = [
... {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2, "species": "Iris-setosa"},
... {"sepal_length": 7.9, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4, "species": "Iris-versicolor"},
... ]
>>> td.load(raw_data)
>>> h = Hyperparameter(k=3, algorithm=Chebyshev(), training=td)
>>> len(td.training)
1
>>> len(td.testing)
1
>>> td.test(h)
>>> print(f"data={td.name!r}, k={h.k}, quality={h.quality}")
data='test', k=3, quality=0.0
"""

__test__ = {name: case for name, case in globals().items() if name.startswith("test_")}
