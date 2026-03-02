import plotly.graph_objects as go

# Создание шаблона графика
template = go.layout.Template()
template.layout.paper_bgcolor = 'white'  # Белый фон
template.layout.font.size = 30  # Размер шрифта для надписей
template.layout.title.font.size = 30  # Размер шрифта для заголовка

# Темно-сервые линии для осей
template.layout.xaxis.gridcolor = 'darkgray'
template.layout.yaxis.gridcolor = 'darkgray'
template.layout.xaxis.linecolor = 'black'
template.layout.xaxis.showline = True
template.layout.yaxis.linecolor = 'black'
template.layout.yaxis.showline = True


if __name__ == '__main__':
    # Пример графика
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[1, 3, 2], mode='lines'),
                    layout=go.Layout(template=template))

    # Отображение графика
    fig.show()