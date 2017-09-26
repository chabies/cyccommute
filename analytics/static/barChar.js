//This script has been modified according to the usage of it for this project as a function
//Source:https://www.sitepoint.com/creating-simple-line-bar-charts-using-d3-js/
function InitChart(data, svg_id, width_num, height_num, color_list, layer_list) {

  var barData = data.valueOf(); // [{"x":seg_id, "y":#}, ..., ]

  var colors = color_list.valueOf() // [color_code, ...,]

  var colorScale = d3.scale.quantize()
      .domain([0, data.length-1])
      .range(colors);

  var vis = d3.select(svg_id),
    WIDTH = width_num,
    HEIGHT = height_num,
    MARGINS = {
      top: 20,
      right: 20,
      bottom: 20,
      left: 50
    },

    xRange = d3.scale.ordinal().rangeRoundBands([MARGINS.left, WIDTH - MARGINS.right], 0.1).domain(barData.map(function (d) {
      return d.x;
    })),


    yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0,
      d3.max(barData, function (d) {
        return d.y;
      })
    ]),

    xAxis = d3.svg.axis()
      .scale(xRange)
      .tickSize(5)
      .tickSubdivide(true),

    yAxis = d3.svg.axis()
      .scale(yRange)
      .tickSize(5)
      .orient("left")
      .tickSubdivide(true).tickFormat(d3.format("d"));


    vis.append('svg:g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + (HEIGHT - MARGINS.bottom) + ')')
    .call(xAxis);

  vis.append('svg:g')
    .attr('class', 'y axis')
    .attr('transform', 'translate(' + (MARGINS.left) + ',0)')
    .call(yAxis);

  vis.selectAll('rect')
    .data(barData)
    .enter()
    .append('rect')
    .attr('x', function (d) {
      return xRange(d.x);
    })
    .attr('y', function (d) {
      return yRange(d.y);
    })
    .attr('width', xRange.rangeBand())
    .attr('height', function (d) {
      return ((HEIGHT - MARGINS.bottom) - yRange(d.y));
    })
    .style('fill', function(d,i){return colorScale(i);})

}