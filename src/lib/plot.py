import matplotlib.pyplot as plt
from pywaffle import Waffle
import io
import base64

plt.switch_backend('Agg')


def get_donut(data, title, color_conditions):
    # initiate figure
    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(aspect="equal"))
    plt.text(0, 0, title, color=color_conditions[data['grade']]['color'], fontsize='medium', fontweight='bold', ha='center', va='center')

    # build data
    circle_shapes = [data['score']]
    circle_colors = [color_conditions[data['grade']]['color']]
    circle_transparency = [1.0]

    current_value = data['score']
    current_grade = color_conditions[data['grade']]
    while current_grade is not None:
        circle_shapes.append(current_grade['max'] - current_value)
        circle_colors.append(current_grade['color'])
        circle_transparency.append(0.2)

        current_value = current_grade['max']
        current_grade = next((v for v in color_conditions.values() if v['min'] == current_value), None)

    circle_width = 0.3
    radius = 0.6 + 3*circle_width

    # plot
    donut = plt.pie(circle_shapes, center=(0, 0), startangle=90, radius=radius, colors=circle_colors)
    plt.setp(donut[0], width=circle_width, edgecolor=None)
    for idx, alpha in enumerate(circle_transparency):
        donut[0][idx].set_alpha(alpha)

    # encode in base64
    memory = io.BytesIO()
    plt.savefig(memory, format='png', transparent=True, bbox_inches='tight')
    memory.seek(0)
    b64 = base64.b64encode(memory.read()).decode('utf-8')
    plt.close()
    return b64


def get_donuts_concentric(data, title, color_conditions):
    # initiate figure
    fig, ax = plt.subplots(figsize=(2, 2), subplot_kw=dict(aspect="equal"))
    plt.title(title, y=1+0.1*(len(data)-1), ha='center', va='center', fontstyle='italic', fontsize='medium')

    circle_width = 0.3
    radius = 0.6
    if len(data) < 4:
        radius += circle_width
    ratio = 0.75
    for circle in data:
        # place label
        plt.text(-0.05, radius - circle_width/2, circle['name'], fontsize='small', ha='right', va='center')

        # build data
        circle_shapes = [circle['score'] * ratio]
        circle_colors = [color_conditions[circle['grade']]['color']]
        circle_transparency = [1.0]

        current_value = circle['score']
        current_grade = color_conditions[circle['grade']]
        while current_grade is not None:
            circle_shapes.append((current_grade['max'] - current_value)*ratio)
            circle_colors.append(current_grade['color'])
            circle_transparency.append(0.2)

            current_value = current_grade['max']
            current_grade = next((v for v in color_conditions.values() if v['min'] == current_value), None)

        circle_shapes.append((1 - ratio)*100)
        circle_colors.append('#000000')
        circle_transparency.append(0.0)

        # plot
        donut = plt.pie(circle_shapes, center=(0, 0), startangle=90, counterclock=False, radius=radius, colors=circle_colors)
        plt.setp(donut[0], width=circle_width, edgecolor=(1, 1, 1, 0.0), linewidth=1)
        for idx, alpha in enumerate(circle_transparency):
            donut[0][idx].set_alpha(alpha)

        radius += circle_width

    # encode in base64
    memory = io.BytesIO()
    plt.savefig(memory, format='png', transparent=True, bbox_inches='tight')
    memory.seek(0)
    b64 = base64.b64encode(memory.read()).decode('utf-8')
    plt.close()
    return b64


def get_lollipop(data, title, color_conditions):
    data_sorted = sorted(data, key=lambda k: k['score'], reverse=True)

    # initiate figure
    fig, ax = plt.subplots(figsize=(len(data_sorted)/2, 2))
    plt.title(title, y=1.2, ha='center', va='center', fontstyle='italic', fontsize='medium')

    # build data
    names = [elt['name'] for elt in data_sorted]
    scores = [elt['score'] for elt in data_sorted]
    colors = [color_conditions[elt['grade']]['color'] for elt in data_sorted]

    # plot
    ax.set_ylim(0, 100)
    plt.grid(which='major', axis='both', color='#7c7c7c', linestyle='dotted', linewidth=0.5)
    for grade, condition in color_conditions.items():
        plt.text(len(data_sorted)-0.3, (condition['min'] + condition['max'])/2, grade, ha='center', va='center', color=condition['color'])
        ax.axhline(y=condition['max'], color='#363636', linestyle='-.', linewidth=1, zorder=1)
    xlabels = ax.get_xticklabels()
    plt.setp(xlabels, rotation=20, horizontalalignment='right')

    ax.vlines(x=names, ymin=0, ymax=scores, colors=colors, linewidths=2, zorder=2)
    ax.scatter(names, scores, c=colors, zorder=2)

    # encode in base64
    memory = io.BytesIO()
    plt.savefig(memory, format='png', transparent=True, bbox_inches='tight')
    memory.seek(0)
    b64 = base64.b64encode(memory.read()).decode('utf-8')
    plt.close()
    return b64


def get_waffle(data, title, border=False):
    nb_columns = 20
    nb_rows = max(sum([v['count'] for v in data.values()]) // nb_columns + 1, 2)
    labels = ['{} ({})'.format(v['name'], v['count']) for v in data.values()]
    values = [v['count'] for v in data.values()]
    colors = [v['color'] for v in data.values()]
    icons = [v['icon-fa'] for v in data.values()]

    # plot
    fig = plt.figure(
        figsize=(6, nb_rows/2),
        linewidth=2,
        FigureClass=Waffle,
        tight=False,
        columns=nb_columns,
        vertical=True,
        block_arranging_style='normal',
        starting_location='NW',
        plot_anchor='S',
        interval_ratio_x=0.2,
        interval_ratio_y=0.2,
        values=values,
        colors=colors,
        icons=icons,
        icon_size=10, icon_legend=True,
        legend={'loc': 'lower center', 'labels': labels, 'ncol': len(labels), 'bbox_to_anchor': (0.5, 1), 'framealpha': 0.0, 'fontsize': 'small'},
    )
    fig.suptitle(title, y=0.88, ha='center', va='center', fontstyle='italic', fontsize='medium')

    # encode in base64
    memory = io.BytesIO()
    if border is True:
        plt.savefig(memory, format='png', edgecolor='black', transparent=True)
    else:
        plt.savefig(memory, format='png', transparent=True)
    memory.seek(0)
    b64 = base64.b64encode(memory.read()).decode('utf-8')
    plt.close()
    return b64
