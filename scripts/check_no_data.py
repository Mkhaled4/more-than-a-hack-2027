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
#
# Will also warn (locally, on every commit) if a data/ or vendor/challenge/data/ folder exists in
# the working tree with anything in it besides its README. Git would not commit it, but AI tools
# can still see it, so it should be moved to ~/mtah-data.
