// (function () {
    function barchart (response) {
        var margin = {top: 30, right: 40, bottom: 40, left: 40},
            width = 600 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;
        
        var x = d3.scale.ordinal()
            .rangeRoundBands([0, width], .2, .15);

        var y = d3.scale.linear()
                .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var barchart = d3.select("#barchart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var json = response
            // [
            // {"date":'11-09-2014', "depth": 6},
            // {"date":'11-10-2014', "depth": 1},
            // {"date":'11-11-2014', "depth": 4}, 
            // {"date":'11-12-2014', "depth": 6},
            // {"date":'11-13-2014', "depth": 1},
            // {"date":'11-14-2014', "depth": 4} 
            // ];
         // d3.json('data/json_sample.json', function(error, data) {
            // var jsondata = data.map(function(d) {return d['station']});
            // if (error) console.warn("error " + error);
            console.log("data " + json);
            x.domain(json.map(function(d) { return d['date'] }));
            // x.domain([0, d3.max(json, function(d) { return d['date']; })])
            y.domain([0, d3.max(json, function(d) { return d.depth; })]).nice();

            barchart.append("text")
                .text("Snow Depth 7-Day Trend")
                .attr("x", (width / 2))
                .attr("y", 0 - (margin.top / 2))
                .attr("class", "title")
                .attr("text-anchor", "middle");

            barchart.append("g")
                .attr("class", "xAxis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            barchart.append("g")
                .attr("class", "yAxis")
                .call(yAxis)
              //`.append("text");
            
            barchart.selectAll(".bar")
                .data(json)
              .enter().append("rect")
                .attr("class", function (d) {
                    //var date = d.date.replace(/\s+/g, '-').toLowerCase();
                    var date = date
                    return "bar " + date   
                })
                .attr("x", function(d) { return x(d.date); })
                .attr("width", x.rangeBand())
                .attr("y", function(d) { return y(d.depth) })
                .attr("height", function (d) { return height - y(d.depth); })
                // .on("mouseover", function (d) { linechart(d); })
                // .on("mouseout", remove_linechart) ;
        // });
    }

    // Here's where we call the function
    // barchart();

// })();

