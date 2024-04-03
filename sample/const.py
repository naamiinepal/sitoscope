GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("O", "Others")]

WATER_TYPE_CHOICES = [
    ("RI", "River"),
    ("BO", "Bottled"),
    ("JA", "Jar"),
    ("LA", "Lake"),
    ("WL", "Wetland"),
    ("WW", "Well Water"),
    ("DB", "Deep Boring"),
    ("PW", "Pond Water"),
    ("ST", "Stream"),
    ("SW", "Spring Water"),
    ("MT", "Tap (Municipal Tap)"),
    ("TA", "Tap (Tanker)"),
    ("TU", "Tap (Tubewell)"),
    ("DH", "Tap (Dhungedhara)"),
    ("BR", "Tap (Boring)"),
    ("FL", "Tap (Filter)"),
    ("WT", "Tap (Water Tank)"),
]

VEGETABLE_CHOICES = [
    ("CU", "Cucumber"),
    ("CA", "Cabbage"),
    ("TO", "Tomato"),
    ("RA", "Radish"),
    ("CR", "Carrot"),
    ("SP", "Spinach"),
    ("CH", "Chilli"),
]

STANDARD_SAMPLE_TYPES = [
    ("W", "Water"),
    ("V", "Vegetable"),
    ("S", "Stool"),
]


IMAGE_TYPE_CHOICES = [("S", "Smartphone"), ("B", "Brightfield")]

# Number of slides per sample
SLIDE_COUNT = 3

STANDARD_SAMPLE_SLIDE_COUNT = 25

# Number of images per slide
IMAGE_COUNT = 15

# Sample default time filter start
DEFAULT_FILTER_RANGE_START = "2021-01-01"

# number of samples for each image type to annotate for inter-annotator analysis
COMMON_ANNOTATION_SAMPLES = 100
