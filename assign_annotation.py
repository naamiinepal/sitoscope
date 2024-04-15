import os
from typing import Optional, Sequence

import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "parasite.settings")
django.setup()


from annotation.models import Annotation, Annotator
from sample.const import COMMON_ANNOTATION_SAMPLES, IMAGE_TYPE_CHOICES
from sample.models import SlideImage


def assign_annotations(
    usernames: Optional[Sequence[str]] = None,
    reference_annotator_username: Optional[str] = None,
    assign_common: bool = True,
    limit: int = COMMON_ANNOTATION_SAMPLES,
):
    """
    A function that assigns annotations to annotators based on certain conditions.
    Parameters:
        usernames: An optional sequence of strings representing usernames to assign annotations to.
        reference_annotator_username: An optional string representing the reference annotator username.
        assign_common: A boolean indicating whether to assign common annotations.
        limit: An integer specifying the limit of common annotations to assign.
    Returns:
        None
    """
    # Get all annotators from username
    annotators = (
        Annotator.objects.filter(user__username__in=usernames)
        if usernames
        else Annotator.objects.all()
    )

    # If there are no annotators, return
    if not annotators.exists():
        print("No annotators found.")
        return

    if assign_common:
        if reference_annotator_username is not None:
            print(f"Using {reference_annotator_username} for common annotations.")
            existing_annotations_for_reference_annotator = Annotation.objects.filter(
                annotator__user__username=reference_annotator_username
            ).values("image")
        else:
            existing_annotations_for_reference_annotator = None

        print(f"{existing_annotations_for_reference_annotator=}")

        annotations = []
        for image_type in IMAGE_TYPE_CHOICES:
            slide_images_to_assign = (
                SlideImage.objects.filter(
                    ~Q(image=""),
                    image_type=image_type[0],
                    approved=True,
                    id__in=existing_annotations_for_reference_annotator,
                )
                if existing_annotations_for_reference_annotator is not None
                else get_random_slide_images(image_type=image_type[0], limit=limit)
            )

            annotations.extend(
                (
                    Annotation(image=slide_image, annotator=annotator)
                    for annotator in annotators
                    for slide_image in slide_images_to_assign
                )
            )
            print(len(annotations))
        Annotation.objects.bulk_create(
            annotations, ignore_conflicts=True, batch_size=512
        )
    else:
        if reference_annotator_username is not None:
            print(
                f"`reference_annotator_username` not used for uncommon annotations. Skipping."
            )

        for image_type in IMAGE_TYPE_CHOICES:
            filter_query = ~Q(image="") & ~Q(
                id__in=Annotation.objects.all().values("image")
            )
            num_slide_images = SlideImage.objects.filter(
                filter_query, approved=True, image_type=image_type[0]
            ).count()
            if num_slide_images < limit * len(annotators):
                msg = (
                    f"Not enough {image_type[1]} slide images: {num_slide_images} "
                    f"to equally assign {limit} annotations to {len(annotators)} annotators."
                )
                raise ValueError(msg)

            for annotator in annotator:
                # Slide Images to assign changes for each annotator ()
                slide_images_to_assign = get_random_slide_images(
                    filter_query=filter_query,
                    image_type=image_type[0],
                    limit=limit,
                )

                anno = tuple(
                    Annotation(image=slide_image, annotator=annotator)
                    for slide_image in slide_images_to_assign
                )

                Annotation.objects.bulk_create(
                    anno, ignore_conflicts=True, batch_size=512
                )


def get_random_slide_images(
    *, filter_query: Optional[Q] = None, limit: Optional[int] = None, **kwargs
):
    """
    Retrieves random slide images based on optional filter query and limit parameters.

    Args:
        filter_query (Optional[Q]): Optional filter query to filter the slide images.
        limit (Optional[int]): Optional limit on the number of slide images to retrieve.
        **kwargs: Additional keyword arguments for filtering the slide images.

    Returns:
        QuerySet: QuerySet of SlideImage objects filtered based on the provided parameters.
    """
    if filter_query is None:
        filter_query = ~Q(image="")
    return SlideImage.objects.filter(filter_query, approved=True, **kwargs).order_by(
        "?"
    )[:limit]


if __name__ == "__main__":
    from argparse import ArgumentParser, BooleanOptionalAction

    parser = ArgumentParser(description="Assign annotations to annotators.")

    parser.add_argument(
        "-a",
        "--annotator",
        nargs="+",
        help="Usernames to be added to annotators",
        default=None,
        dest="usernames",
    )

    parser.add_argument(
        "-r",
        "--reference-annotator",
        help="Reference annotator username",
        default=None,
        dest="reference_annotator_username",
    )

    parser.add_argument(
        "-c",
        "--assign-common",
        action=BooleanOptionalAction,
        help="Assign common annotations to annotators",
        default=True,
    )

    parser.add_argument(
        "-l",
        "--limit",
        help="Number of common annotations to assign",
        type=int,
        default=COMMON_ANNOTATION_SAMPLES,
    )

    args = parser.parse_args()

    assign_annotations(**vars(args))

    print("Done!")
