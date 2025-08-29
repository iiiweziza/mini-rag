from enum import Enum 

class VectorDBEnums(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    EUCLIDEAN = "euclidean"
    COSINE = "cosine"  # most common 
    DOT = "dot"