# ws:dead: decide which frames are dead ball (D).
#
# Output: boolean mask over frames, True where the ball is dead.
#
# Ideas:
# - ball out of bounds (pitch is 105.3 x 68 m)
# - players static / slow for a while
# - Smart Tagging set pieces and restarts (evidence, not truth; throw-ins have team N/A)
# - official baseline: dead wherever the ball is not observed. Start here.
#
# Methods are selected via the `deadball:` section of the config.
