odoo.define('booking.website1', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var qweb = core.qweb;

ajax.loadXML('/website_calendar_booking/static/src/xml/website_calendar_booking_modal1.xml', qweb);

$(function() {
  var date = new Date();
  var d = date.getDate();
  var m = date.getMonth();
  var y = date.getFullYear();
  console.log(y + "-" + m + "-" + d);

  $("#calendar").fullCalendar({
    header: {
      left: "prev,next today",
      center: "title",
      right: "month,agendaWeek,agendaDay"
    },
    themeSystem: "bootstrap3",

    events: [
      {
        title: "Sales Meeting",
        start: new Date(y, m, d, 10, 30),
        end: new Date(y, m, d, 11, 30),
        allDay: false
      },
      {
        title: "Marketing Meeting",
        start: new Date(y, m, d, 13, 30),
        end: new Date(y, m, d, 14, 30),
        allDay: false
      },
      {
        title: "Production Meeting",
        start: new Date(y, m, d, 15, 30),
        end: new Date(y, m, d, 16, 30),
        allDay: false
      }
    ]
  });

  $(".fc-today-button").click(function() {
    alert("1");
  });
});



});