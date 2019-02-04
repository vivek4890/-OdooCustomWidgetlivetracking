odoo.define('base_trip_mgmt.page', function(require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var ControlPanel = require('web.ControlPanel');

    var HomePage = AbstractAction.extend({

        events: {

            'click .addFilter': '_showFilteredTrips',
            'click .trip_dt': '_showTripInfo',
        },

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
        },

        start: function() {
            var self = this;
            var trip_data = this._rpc({
                    model: 'base.sd.trip',
                    method: 'data_for_live_traking',
                })
                .then(function(res) {
                    // console.log('');
                    // console.log(res);
                    if (res.loaded_trip_dic) {
                        self.$el.html(QWeb.render("HomePageTemplate", {
                            'vechile_data': res.loaded_trip_dic.vechile_data,
                            'driver_data': res.loaded_trip_dic.driver_data,
                            'tr_data': res.loaded_trip_dic.trips
                        }));
                    }
                });

            var ele = $('.trip_dt')[0];
            console.log(ele);

            return $.when(trip_data, this._super.apply(this, arguments));

        },

        _showFilteredTrips: function(event) {
            var self = this;
            var data_arr = [];
            var date = $('.filter_section').find('input');
            // console.log(date);
            $('.filter_section').find('input').each(function(i) {
                data_arr.push(this.value);
            });
            $('.filter_section').find('select').each(function(i) {
                data_arr.push(this.value);
            });
            // console.log(data_arr);
            $('.icons').empty();
            if (data_arr[0] != ""){
                $('.icons').prepend('<i class="far fa-calendar icon"></i>&nbsp;&nbsp;');
            }
            if (data_arr[1] != ""){
                $('.icons').prepend('<i class="fas fa-sort-numeric-up icon"></i></i>&nbsp;&nbsp;');
            }
            if (data_arr[2] != ""){
                $('.icons').prepend('<i class="fas fa-truck icon"></i>&nbsp;&nbsp;');
            }
            if (data_arr[3] != ""){
                $('.icons').prepend('<i class="fas fa-dharmachakra"></i>&nbsp;&nbsp;');
            }
            $('.icons').append('<div class="break" style="height:15px;"></div');
            
            // console.log('-++++++++++++-', data_arr);
            this._rpc({
                model: 'base.sd.trip',
                method: 'filter_trip_data',
                args: [{
                    'scheduled_date': data_arr[0],
                    'vehicle_num': data_arr[1],
                    'trip_name': data_arr[2],
                    'driver_name': data_arr[3]
                }]
            }).then(function(result) {
                if (result) {
                    // console.log('------------result------------', result);
                    $('.trips_data').empty();
                    $('.trips_data').append('<div class="trips"></div>');
                    for (var i = 0; i < result.length; i++) {
                        var html = '<span class="tag badge trip_dt" id="' + result[i].id + '">Trip: ' + result[i].id + '</span>';
                        // console.log(html);
                        $('.trips').append(html);
                    }
                    if ($('.trip_dt').length > 0) {
                        $('.trip_dt')[0].click();
                        $('.click-btn2').addClass('active');
                        $('.trip_detail').addClass('active');
                    }
                }
            });


        },

        _showTripInfo: function(event) {

            var self = this;
            // console.log(event);
            var id = event.toElement.id;

            // console.log(id);
            this._rpc({
                    model: 'base.sd.trip',
                    method: 'data_for_live_traking',
                    args: [{
                        'id': id
                    }]
                })
                .then(function(res) {
                    // console.log(res.trip);
                    if (res.trip) {
                        // console.log('-------------------------', res.trip)
                        $('.trip_detail').empty();
                        $('.trip_detail').append('<h2 class="text-center"> Trip Details </h2>');
                        var id = '<span class="tag badge trip_dtd" id="trip-info" >Trip Id: ' + res.trip.id + '</div>';
                        var name = '<span class="tag badge trip_dtd" id="trip-info" >Trip Name: ' + res.trip.name + '</div>';
                        var cap = '<span class="tag badge trip_dtd"  id="trip-info" >Vechile Capacity: ' + res.trip.vehicle.cap + '</span>';
                        var loaded_qty = '<span class="tag badge trip_dtd" id="trip-info" ">Loaded Quantity:  ' + res.trip.vehicle.loaded_qty + '</span>';
                        var model = '<span class="tag badge trip_dtd" id="trip-info" >Vechile Reg No: ' + res.trip.vehicle.model + '</span>';
                        var reg_no = '<span class="tag badge trip_dtd" id="trip-info" >Requird Quantity: ' + res.trip.vehicle.reg_no + '</span>';
                        var required_qty = '<span class="tag badge trip_dtd" id="trip-info" >Vechile Model: ' + res.trip.vehicle.required_qty + '</span>';
                        $('.trip_detail').append(id);
                        $('.trip_detail').append(name);
                        $('.trip_detail').append(cap);
                        $('.trip_detail').append(loaded_qty);
                        $('.trip_detail').append(model);
                        $('.trip_detail').append(reg_no);
                        $('.trip_detail').append(required_qty);
                        // $('.click-btn2').find('i.fa.fa-arrow-right')[0].click();
                        // setTimeout(function () {
                        //     $('.click-btn2').find('i.fa.fa-arrow-right')[0].click();
                        // }, 500);
                        var n = 25;
                        var dot = 40;
                        var line = 20;
                        // var mem = $('.main')[0];
                        // console.log('8',mem);
                        var directionsService = new google.maps.DirectionsService();
                        var directionsDisplay = new google.maps.DirectionsRenderer();
                        var chicago = new google.maps.LatLng(41.850033, -87.6500523);
                        var mapOptions = { zoom:7, mapTypeId: google.maps.MapTypeId.ROADMAP, center: chicago }
                        var map = new google.maps.Map($('.dummy-map')[0], mapOptions);
                        directionsDisplay.setMap(map);
                        $('.left_animate').empty();
                        $('.right_animate').empty();
                        $('.trip_animate').empty();
                        $('.left_animate').append("<button class='btn btn-secondary float-left' id='left-button'><i class='fas fa-angle-left arrow_btn'></i></button>");
                        $('.right_animate').append("<button class='btn btn-secondary float-right' id='right-button'><i class='fas fa-angle-right arrow_btn'></i></button>");
                        for (var i = 0; i < n; i++) {
                            var dot_html = "<span class='dot' style = 'width:" + dot + "px;height:" + dot + "px';>" + (i + 1) + "</span>";
                            // console.log(dot_html);
                            $('.trip_animate').append(dot_html);
                            $('.trip_animate').append("<span>&nbsp;&nbsp;</span>");
                            if (i != n - 1) {
                                var line_html = "<i class='fas fa-long-arrow-alt-right'></i>";
                                $('.trip_animate').append(line_html);
                            }
                            $('.trip_animate').append("<span>&nbsp;&nbsp;</span>");
                        }
                    }
                    $('#right-button').click(function() {
                        event.preventDefault();
                        $('.trip_animate').animate({
                            scrollLeft: "+=100px"
                        }, 100);
                    });
                    $('#left-button').click(function() {
                        event.preventDefault();
                        $('.trip_animate').animate({
                            scrollLeft: "-=100px"
                        }, 100);
                    });

                });

        }

    });

    core.action_registry.add('page_live', HomePage);
    return HomePage;

});