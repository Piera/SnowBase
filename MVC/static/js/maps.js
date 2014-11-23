        var geocoder;
        var map;
        var lat;
        var lng;
        var positions = [];
        var coordinates_array = [];
        var heatmap;
        var bounds;
        var gradient;
        $(document).ready(function() {
        
          initialize();

          // -------  Text alert in progress
          $("#test_alert").click(function() {
            $.post(
              "/alert",
              {
                alert: 1,
                station: 5
              },
              function (response) {
                console.log(response);
                console.log("Got it");
               },
               "json"
            );
          });

          // ---------- End Text alert

          // // ---------- Chart rendering

          // $("#test_chart").click(function() {
          //   $.get(
          //     "/charts",
          //     {
          //       station: "SQUAW VALLEY G.C."
          //     },
          //     function (response) 
          //     {
          //       console.log(response);
          //       console.log("Got it");
          //       $.getScript("static/charts.js", function(){
          //       alert("Script loaded and executed.");
          //       barchart(response);
          //       });
          //     },
          //     "json"
          //   );
          // });
            
          // // ---------- End charts

          // ---------- See all points on heatmap

          $("#see_all").click(function() {
            clearAllMap(map);
            coordinates_array = [];
            if (heatmap) {
            heatmap.setMap(null);
             }

            $.post(
              "/see_all",
              {
                button: 1
              },
              function (response) {
                console.log(response);
                console.log("Got it");
                var all_map = [];
                for (var i in response)
                  {
                    var coordinates = new google.maps.LatLng(response[i]['lat'],response[i]['lng']);
                    var point_weight = response[i]['depth']*1.5;
                    all_map.push(coordinates);
                    coordinates_array.push({location: coordinates, weight: point_weight});
                    console.log("Heatmap array: " + coordinates_array);
                    // var marker_depth = response[i]['depth'];
                    // console.log("Marker_depth: " + marker_depth);
                  }

                  bounds = new google.maps.LatLngBounds();
                    for(i=0;i<coordinates_array.length;i++) {
                     // bounds.extend(all_map.getPosition());
                     bounds.extend(all_map[i]);
                    }
                  map.fitBounds(bounds);
                  // console.log("Positions array: " + positions);
                  heatmap = new google.maps.visualization.HeatmapLayer({
                  data: coordinates_array,
                  radius: 5,
                  gradient: gradient,
                  dissipating: true
                  });
                  heatmap.setMap(map);

               },
               "json"
            );
            });

          // ---------- End see all points on heatmap

          // ---------- Location based snow report

          // ---------- Accept return as a submission event

          // $('#find_snow').keydown(function(event){    
          //     if(event.keyCode==13){
          //        $('#find_snow').trigger('click');
          //     }
          // });

          // ---------- End, accept return as a submission event         

          $("#find_snow").click(function() {
            clearAllMap(map);
            coordinates_array = [];
            if (heatmap) {
            heatmap.setMap(null);
             }
            var address = $("#address").val()
            geocoder.geocode( { 'address': address}, function(results, status) {
              if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                map.setZoom(8);
                var marker = new google.maps.Marker({
                    map: map,
                    position: results[0].geometry.location,
                    title: address
                    });
                positions.push(marker);
            } else {
                alert('Geocode was not successful for the following reason: ' + status);
              }
              var lat = results[0].geometry.location.lat();
              var lng = results[0].geometry.location.lng();
              // console.log(lat, lng);

              $.post(
                "/report",
                {
                  lat: lat,
                  lng: lng
                },
                function (response) {
                  // console.log(response['closest'][2]['lat']);
                  function getCircle(depth) {
                                return {
                                  path: google.maps.SymbolPath.CIRCLE,
                                  fillColor: 'blue',
                                  fillOpacity: .5,
                                  // scale: Math.pow(2.2, depth) / Math.PI,
                                  scale: depth*10/10000,
                                  strokeColor: 'blue',
                                  strokeWeight: .7
                                };
                            }
                  var infowindow = null;
                  var image = ('static/img/marker_blue.png');
                  // var image = '{{ url_for('static', filename='marker_blue.png') }}';
                  infowindow = new google.maps.InfoWindow();
                  for (var i in response['closest'])
                  {
                    // $('#snow_report').html("this is deep: " + response[i].depth + "<br>");
                    // console.log("Coordinates: " + response['closest'][i]['lat'],response['closest'][i]['lng']);
                    var coordinates = new google.maps.LatLng(response['closest'][i]['lat'],response['closest'][i]['lng']);
                    var point_weight = response['closest'][i]['depth']*1.5;
                    coordinates_array.push({location: coordinates, weight: point_weight});
                    // console.log("Heatmap array: " + coordinates_array);
                    var marker_depth = response['closest'][i]['depth'];
                    // console.log("Marker_depth: " + marker_depth);
                    marker = new google.maps.Marker
                      ({
                    map: map,
                    position: coordinates,
                    icon: image,
                    // icon: getCircle(marker_depth),
                    animation: google.maps.Animation.DROP,
                    title: (response['closest'][i]['name'] + ", " + "Snow depth: " + response['closest'][i]['depth'] + " in."),
                    info: ("<strong>Station:</strong> " + response['closest'][i]['name'] +  "<br><strong>Elevation:</strong> " + response['closest'][i]['ele'] + "<br><strong>Distance:</strong> " + response['closest'][i]['dist'] + " mi." + "<br><strong>Snow depth:</strong> " + response['closest'][i]['depth'] + " in." + "<br><strong>Depth change:</strong> " + response['closest'][i]['depth_change'] + " in.")
                     });

                    google.maps.event.addListener(marker, 'click', function() {
                          //marker.info.open(map, this);
                          infowindow.setContent(this.info);
                          infowindow.open(map, this);
                      });

                    positions.push(marker);

                  }


                  bounds = new google.maps.LatLngBounds();
                    for(i=0;i<positions.length;i++) {
                     bounds.extend(positions[i].getPosition());
                    }
                  map.fitBounds(bounds);
                  // console.log("Positions array: " + positions);
                  heatmap = new google.maps.visualization.HeatmapLayer({
                  data: coordinates_array,
                  radius: 25,
                  gradient: gradient,
                  dissipating: true
                  });
                  heatmap.setMap(map);

                  // --------- Narrative snow reports

                  // $('#snow_report').html("<br><h4>Snow Report:</h4><ul><li><h5>The two stations closest to this location are the " + response['closest'][0]['name'] + " station that is " + response['closest'][0]['dist'] + " miles away, with " + response['closest'][0]['depth'] + " inches of snow, and the " + response['closest'][1]['name'] + " station that is " + response['closest'][1]['dist'] + " miles away, with " + response['closest'][1]['depth'] + " inches of snow.</li></ul></h5>")

                  // $('#snow_report').append(
                  //   "<ul><li><h5>Of these closest stations, the stations reading most snow pack are the " + response['deepest'][0]['name'] + " station that is " + response['deepest'][0]['dist'] + " miles away, with " + response['deepest'][0]['depth'] + " inches of snow, and the " + response['deepest'][1]['name'] + " station that is " + response['deepest'][1]['dist'] + " miles away, with " + response['deepest'][1]['depth'] + " inches of snow.</h5></li></ul>")

                  // $('#snow_report').append(
                  //   "<ul><li><h5>The stations with the most new snow are the " + response['most new'][0]['name'] + " station that is " + response['most new'][0]['dist'] + " miles away, with " + response['most new'][0]['depth'] + " inches of total snow, including " + response['most new'][0]['depth_change'] + " inches of new snow, and the " + response['most new'][1]['name'] + " station that is " + response['most new'][1]['dist'] + " miles away, with " + response['most new'][1]['depth'] + " inches of total snow, including " + response['most new'][0]['depth_change'] + " inches of new snow.</h5></li></ul><br>")

                  // --------- End, narrative snow reports

                  // --------- Table report

                  $('#stations_data').html('')

                  var table_headers = "<tr class = 'snow_data' id='snow_data_table'><td class='column_header' id='stations'><center><strong>Station</center></strong></td><td class='column_header' id='distances'><center><strong>Distance</center></strong></td><td class='column_header' id='elevations'><center><strong>Elevation</center></strong></td><td class='column_header' id='depths'><center><strong>Snow Depth</center></strong></td><td class='column_header' id='depth changes'><center><strong>Change in Snow Depth</center></strong></td></tr>"

                  $('#stations_data').append(table_headers)

                  for (var i = 0; i < response['closest'].length; i++) {
                  $('#stations_data').append("<tr><td>" + response['closest'][i]['name'] + "</td><td><center>" + response['closest'][i]['dist'] + " mi. </center></td><td><center>" + response['closest'][i]['ele'] + " ft. </center></td><td><center>" + response['closest'][i]['depth'] + " in. </center></td><td><center>" + response['closest'][i]['depth_change'] + " in. </center></td></tr>")

                  // ---------- Chart rendering 

                  $('#stations_data').on('click', 'tr', function(event){
                    event.stopImmediatePropagation();
                    var table_data = $('td:first', this).text();
                    console.log('You clicked on this table data: ' + table_data);
                    getChart(table_data);
                    });

                    function getChart(table_data) {
                      $.get(
                        '/charts',
                        {
                          station: table_data
                        },
                        function (response) 
                        {
                          console.log('This is the chart data: '+ response);
                          $.getScript("static/js/charts.js", function(){
                          alert("Script loaded and executed.");
                          barchart(response);
                          });
                        },
                        "json"
                      );
                    }
            
                  // ---------- End charts

                  // --------- End, table report

                  }

                },
                "json"
              );
            });
          });
        });

        // ---------- End location based snow report

        // ---------- Map clearing

        function clearAllMap(map) {
          if (positions) 
          {
            for (var i = 0; i < positions.length; i++) 
              {
                positions[i].setMap(null)
                console.log("Positions: " + positions[i])
              }
              positions = [];
              } else 
              {
              console.log("hi Piera");
              }
          }

        // ---------- End map clearing

        // ---------- Map initialization & settings

        function initialize() {
         var styles = [
                {
              featureType: "all",
              stylers: [
                { saturation: -80 }
              ]
            },{
              featureType: "road.arterial",
              elementType: "geometry",
              stylers: [
                { hue: "#00ffee" },
                { saturation: 70 }
              ]
            },{
              featureType: "poi.business",
              elementType: "labels",
              stylers: [
                { visibility: "off" }
              ]
            }
              ];

          gradient = [
            'rgba(0, 255, 255, 0)',
            'rgba(0, 255, 255, 1)',
            'rgba(0, 191, 255, 1)',
            'rgba(0, 127, 255, 1)',
            'rgba(0, 63, 255, 1)',
            'rgba(0, 0, 255, 1)',
            'rgba(0, 0, 223, 1)',
            'rgba(0, 0, 191, 1)',
            'rgba(0, 0, 159, 1)',
            'rgba(0, 0, 127, 1)',
            'rgba(63, 0, 91, 1)',
            'rgba(127, 0, 63, 1)',
            'rgba(191, 0, 31, 1)',
            'rgba(255, 0, 0, 1)'
          ]

          geocoder = new google.maps.Geocoder();
          var styledMap = new google.maps.StyledMapType(styles,
             {name: "Styled Map"});
          var latlng = new google.maps.LatLng(38.48323, -109.2896);
          var mapOptions = {
            zoom: 5,
            center: latlng,
            mapTypeControlOptions: 
             {
            mapTypeId: [google.maps.MapTypeId.TERRAIN, 'map_style']
             },
            disableDefaultUI: true,
            panControl: true,
            zoomControl: true,
            scaleControl: false,
            mapTypeControl: true,
            scrollwheel: false

          }
          map = new google.maps.Map($('#map-canvas').get(0), mapOptions);
          map.mapTypes.set('map_style', styledMap);
          map.setMapTypeId('map_style');

          }

          // ---------- End map initialization & settings