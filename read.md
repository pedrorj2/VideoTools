# VideoTools

VideoTools is a repository containing a set of useful Python-based tools to automate video management and processing tasks. These utilities are designed to simplify common workflows related to video file organization, orientation detection, metadata processing, and more.

## Tools

### 1. **video_orientation**

The `video_orientation` tool automatically sorts video files into their respective folders based on their orientation:

- Horizontal
- Vertical

#### How it works:

- Analyzes video files using metadata (with `pymediainfo`) to determine the actual orientation.
- Accurately identifies videos even if rotation metadata is incorrect or non-standard.
- Moves video files into their respective folders (`horizontal` or `vertical`) for easier management and further processing.

#### Dependencies:

- Python 3.x
- pymediainfo
- MediaInfo (for parsing video metadata)

Install the Python dependencies using pip:

```bash
pip install pymediainfo
```

Download and install [MediaInfo](https://mediaarea.net/en/MediaInfo) separately.

#### Usage:

```bash
python video_orientation_filter.py
```

Ensure you have installed the required dependencies listed above before running the script. Then, move the folder with your videos to the input folder and then edit the input and output routes as needed.

---

## Future tools

More utility scripts and tools will be added if I need them myself, addressing various video processing tasks to enhance productivity and streamline your video management workflow.