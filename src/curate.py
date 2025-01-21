"""curate dataset with fiftyone"""

import os

import fiftyone as fo
import fiftyone.zoo as foz
import numpy as np
from fiftyone import ViewField as F
from sklearn.metrics.pairwise import cosine_similarity

from config import CONFIG


def curate_dataset():
    """
    Find and mark duplicate images using FiftyOne AI.
    """
    images_folder = os.path.join(os.getcwd(), "dataset")
    img_count = len(os.listdir(images_folder))
    batch_size = min(250, img_count)

    # Check for invalid files
    non_images = [
        f
        for f in os.listdir(images_folder)
        if not f.lower().endswith(CONFIG["files"]["supported_types"])
    ]
    if non_images:
        raise ValueError(
            f"Found non-image file {non_images[0]} - Only image files are supported"
        )
    elif img_count == 0:
        raise ValueError(f"No images found in {images_folder}")

    print("\nAnalyzing dataset...\n")
    dataset = fo.Dataset.from_dir(images_folder, dataset_type=fo.types.ImageDirectory)
    model = foz.load_zoo_model(CONFIG["curation"]["model_name"])
    embeddings = dataset.compute_embeddings(model, batch_size=batch_size)

    batch_embeddings = np.array_split(embeddings, batch_size)
    similarity_matrices = []
    max_size_x = max(array.shape[0] for array in batch_embeddings)
    max_size_y = max(array.shape[1] for array in batch_embeddings)

    for batch_embedding in batch_embeddings:
        similarity = cosine_similarity(batch_embedding)
        # Pad with zeros for np.concatenate
        padded_array = np.zeros((max_size_x, max_size_y))
        padded_array[0 : similarity.shape[0], 0 : similarity.shape[1]] = similarity
        similarity_matrices.append(padded_array)

    similarity_matrix = np.concatenate(similarity_matrices, axis=0)
    similarity_matrix = similarity_matrix[
        0 : embeddings.shape[0], 0 : embeddings.shape[0]
    ]

    similarity_matrix = cosine_similarity(embeddings)
    similarity_matrix -= np.identity(len(similarity_matrix))

    dataset.match(F("max_similarity") > CONFIG["curation"]["similarity_threshold"])
    dataset.tags = ["delete", "has_duplicates"]

    id_map = [s.id for s in dataset.select_fields(["id"])]
    samples_to_remove = set()
    samples_to_keep = set()

    for idx, sample in enumerate(dataset):
        if sample.id not in samples_to_remove:
            # Keep the first instance of two duplicates
            samples_to_keep.add(sample.id)

            dup_idxs = np.where(
                similarity_matrix[idx] > CONFIG["curation"]["similarity_threshold"]
            )[0]
            for dup in dup_idxs:
                # We kept the first instance so remove all other duplicates
                samples_to_remove.add(id_map[dup])

            if len(dup_idxs) > 0:
                sample.tags.append("has_duplicates")
                sample.save()
        else:
            sample.tags.append("delete")
            sample.save()

    # Configure and launch the UI
    sidebar_groups = fo.DatasetAppConfig.default_sidebar_groups(dataset)
    for group in sidebar_groups[1:]:
        group.expanded = False
    dataset.app_config.sidebar_groups = sidebar_groups
    dataset.save()

    session = fo.launch_app(dataset)
    print("❗ Wait a minute for the session to load.")
    print("❗ When ready, you'll see a grid of your images.")
    print("❗ Enable 'sample tags' on the left to see images marked for deletion.")
    print(
        "❗ Mark images with 'delete' tag by selecting them and pressing the tag icon."
    )
    input("Press Enter when done to save changes: ")

    print("Saving...")

    marked = [s for s in dataset if "delete" in s.tags]
    dataset.delete_samples(marked)

    # Export and replace original folder
    project_subfolder = "curated"
    export_path = os.path.join(images_folder, project_subfolder)
    dataset.export(export_dir=export_path, dataset_type=fo.types.ImageDirectory)

    # Replace original folder with curated images
    temp_suffix = "_temp"
    os.rename(images_folder, images_folder + temp_suffix)
    os.rename(
        os.path.join(images_folder + temp_suffix, project_subfolder), images_folder
    )
    os.rmdir(images_folder + temp_suffix)

    session.refresh()
    fo.close_app()

    print(
        f"\nRemoved {len(marked)} images. Dataset now contains {len(os.listdir(images_folder))} images."
    )
