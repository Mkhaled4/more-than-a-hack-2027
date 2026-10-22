# Guard used by .githooks/pre-commit and by CI.
#
#   python scripts/check_no_data.py <file> [<file> ...]    -> exit 1 if any file is refused
#
# Will refuse:
# - anything under data/ or outputs/ (except outputs/.gitkeep)
# - data file types: *.mp4, *_atd.txt, *_atd.xml, *_smart_tagging.xml, *_homography.csv,
#   *_possession_gt*.csv, *.pkl, *.npz, *.npy, *.parquet, *.pdf, ...
# - any file larger than 5 MB
# - Jupyter notebooks that still contain cell outputs (outputs can show real rows)
