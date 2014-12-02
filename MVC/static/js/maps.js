var geocoder;
var map;
var lat;
var lng;
var positions = [];
var hover_markers = [];
var coordinates_array = [];
var heatmap;
var bounds;
var gradient;

$(document).ready(function() {

// ---------- Initialize the map

  initialize();

  // ---------- See all points on heatmap

  $("#see_all").click(function() {
    clearAllMap(map);
    coordinates_array = [];
    if (heatmap) {
     heatmap.setMap(null);
    }

    $.get(
      "/see_all", {
        button: 1
      },
      function (response) {
        var all_map = [];
        for (var i in response) {
            var coordinates = new google.maps.LatLng(response[i]['lat'],response[i]['lng']);
            var point_weight = response[i]['depth']*1.5;
            all_map.push(coordinates);
            coordinates_array.push({location: coordinates, weight: point_weight});
        }
        bounds = new google.maps.LatLngBounds();
        for(i=0;i<coordinates_array.length;i++) {
          bounds.extend(all_map[i]);
        }
        map.fitBounds(bounds);
        heatmap = new google.maps.visualization.HeatmapLayer ({
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

  // ---------- Main functionality: create location based snow report      

  $('#address-form').submit(function(evt) {
    evt.preventDefault();  
    clearAllMap(map);
    coordinates_array = [];
    if (heatmap) {
      heatmap.setMap(null);
    }
    var address = $("#address").val()

    // ---------- Geocode user input

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

    // ---------- End geocode user input

      $.get(
        "/report", {
          lat: lat,
          lng: lng
        },
        function (response) {
          var infowindow = null;
          var image = ('static/img/marker_blue.png');
          infowindow = new google.maps.InfoWindow();

          // --------- Plot map markers and create info windows for markers on click

          for (var i in response['closest']) {
            var coordinates = new google.maps.LatLng(response['closest'][i]['lat'],response['closest'][i]['lng']);
            var point_weight = response['closest'][i]['depth']*1.5;
            coordinates_array.push({location: coordinates, weight: point_weight});
            marker = new google.maps.Marker ({
              map: map,
              position: coordinates,
              icon: image,
              animation: google.maps.Animation.DROP,
              title: (response['closest'][i]['name'] + ", " + "Snow depth: " + response['closest'][i]['depth'] + " in."),
              info: ("<i class='glyphicon glyphicon-phone'></i>&nbsp;&nbsp;Get a text alert when<br>" + response['closest'][i]['name'] + " station<br>receives new snow!<br><strong>Text " + response['closest'][i]['text-code'] + " to (510) 447-1579</strong>")
            });
            google.maps.event.addListener(marker, 'click', function() {
              infowindow.setContent(this.info);
              infowindow.open(map, this);
            });
            positions.push(marker);
          }

          // --------- End plot map markers and create info windows for markers on click

          // --------- Create fitbounds and heatmaps

          bounds = new google.maps.LatLngBounds();
          for(i=0;i<positions.length;i++) {
            bounds.extend(positions[i].getPosition());
          }
          map.fitBounds(bounds);
          heatmap = new google.maps.visualization.HeatmapLayer ({
            data: coordinates_array,
            radius: 30,
            gradient: gradient,
            dissipating: true
          });
          heatmap.setMap(map);

          // --------- End fitbounds and heatmaps

          // --------- Remove home page & draw report elements

          $('#home-row').removeClass("tall")
          $('#home-div').remove()
          $('#stations_data').html('')
          $('#text-info').html('')
          $('#time-stamp').html('')
          $('#time-stamp').append("  Last update: " + response['time_stamp'] + " UTC -8:00 (PST)").addClass("padded-info")
          var table_headers = "<thead><tr class = 'snow_data' id='snow_data_table'><td class='column_header' id='stations'><center><strong>Station</center></strong></td><td class='column header' id='text code'><center><span class='glyphicon glyphicon-phone'></span></center></td><td class='column_header' id='distances'><center><strong>Distance</center></strong></td><td class='column_header' id='elevations'><center><strong>Elevation</center></strong></td><td class='column_header' id='depths'><center><strong>Snow Depth</center></strong></td><td class='column_header' id='Snow Density'><center><strong>Snow Density</strong></center></td></tr><thead>"
          $('#stations_data').append(table_headers)
          $('#text-info').append("<center>Text any station code to (510) 447-1579 to receive a text alert when there is new snow!</center>").addClass("padded-info")
          for (var i = 0; i < response['closest'].length; i++) {
            var density;
            if (response['closest'][i]['density'] === "No Data") {
              density = "No Data"
            } else {
              density = (response['closest'][i]['density'] + "%");
          }
          $('#stations_data').append("<tr><td>" + response['closest'][i]['name'] + "</td><td><center><span class='badge'>" + response['closest'][i]['text-code'] + "</span></center></td><td><center>" + response['closest'][i]['dist'] + " mi. </center></td><td><center>" + response['closest'][i]['ele'] + " ft. </center></td><td><center>" + response['closest'][i]['depth'] + " in. </center></td><td><center>" + density + "</center></td></tr>");
          
          // --------- End remove home page & draw report elements
          
          // ---------- d3 Chart rendering and chart hover function 

          getChart(response['closest'][0]['name']);
          $('#stations_data').on('hover', 'tr', function(event) {
            event.stopImmediatePropagation();
            var table_data = $('td:first', this).text();
            if (table_data != 'Station') {
              getChart(table_data);
            } 
          });

            function getChart(table_data) {
              $.get(
                '/charts', {
                  station: table_data
                },
                function (response) {
                  $.getScript("static/js/charts.js", function(){
                    $("#barchart_depth").empty();
                    $("#barchart_density").empty();
                    barchart_depth(response);
                    barchart_density(response);
                    if (hover_markers.length != 0) {
                      hover_markers[0].setMap(null);
                    }
                    hover_markers=[];
                    var hover_marker = ('static/img/white-google-map-pin-md.png');
                    var hover_coordinate = new google.maps.LatLng(response[0]['lat'],response[0]['lng']);
                    marker = new google.maps.Marker ({
                      map: map,
                      position: hover_coordinate,
                      icon: hover_marker
                    });
                    hover_markers.push(marker);
                  });
                },
                "json"
              );
            }
          // ---------- d3 Chart rendering and chart hover function
          }
        },
        "json"
      );
    });
  });
  // ---------- End of main functionality: create location based snow report 
});

// ---------- End map initialization

// ---------- Map clearing function

function clearAllMap(map) {
  if (positions.length !=0) {
    for (var i = 0; i < positions.length; i++) {
      positions[i].setMap(null)
    }
    positions = [];
    } else {
      console.log("Nothing to clear");
    }
  if (hover_markers.length != 0) {
    hover_markers[0].setMap(null);
  }
  hover_markers=[];
}

// ---------- End map clearing function

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
  var styledMap = new google.maps.StyledMapType(styles, {name: "Styled Map"});
  var latlng = new google.maps.LatLng(38.48323, -109.2896);
  var mapOptions = {
      zoom: 5,
      center: latlng,
      mapTypeControlOptions: {
        mapTypeId: [google.maps.MapTypeId.TERRAIN, 'map_style']
      },
      disableDefaultUI: true,
      panControl: false,
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