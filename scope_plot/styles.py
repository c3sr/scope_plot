from cycler import cycler

linestyles = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot']*2
markers = ["circle", "square", "triangle", "asterisk",
           "circle_x", "square_x", "inverted_triangle", "diamond"]
colors = ['#E24A33', '#348ABD', '#988ED5', '#777777',
'#FBC15E', '#8EBA42', '#FFB5B8', '#7F7F7F']

cycles = cycler('color', ['#E24A33', '#348ABD', '#988ED5', '#777777',
                          '#FBC15E', '#8EBA42', '#FFB5B8', '#7F7F7F',
                          '#7F7F7F', '#FFB5B8', '#8EBA42', '#FBC15E',
                            '#777777', '#988ED5', '#348ABD', '#E24A33'])
