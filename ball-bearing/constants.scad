epsilon = 0.01;

ball_r = 2.5; // 5mm steel balls
groove_ball_ratio = 1.03; // hole is 3% larger than the ball
pitch_r = 10; // distance from center to ball centers
num_balls = 8;

// distance between ball top and cage top
cage_top_extension = 1.15;

// distance from ball center to edge of race
race_bore_offset = 1.8;
race_outer_wall = 2.5;  // material beyond groove on outer edge
race_inner_wall = 2.5;  // material from inner groove edge to inner edge
race_top_extension = 1.15; // from the top fo the cage to the top of the races

groove_r = ball_r * groove_ball_ratio;
