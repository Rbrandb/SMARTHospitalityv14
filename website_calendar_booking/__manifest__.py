{
    'name': "Online Reservation System",
    'version': "1.0.96",
    'author': "SMART",
    'category': "Tools",
    'summary': "Allow website users to book reservation from the website",
    'license':'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/access_security.xml',
        'data/data.xml',
        'data/cron_job.xml',
        'data/pax_person_data.xml',
        'data/dashboard_data.xml',
        'data/time_day_data.xml',
        'views/company.xml',
        'views/reservation_event.xml',
        'views/table_event.xml',
        'views/dashboard_views.xml',
        'views/home_reservation.xml',
        'views/res_config_settings_views.xml',
        'views/time_slot_share.xml',
        # 'views/pax_person.xml',

        # 'views/table_time_slot.xml',
        'views/time_slot_dates.xml',
        'views/time_event.xml',
        'views/website_calendar_views.xml',
        'views/website_calendar_booking_templates.xml',

    ],
    'demo': [],
    'depends': ['base','website', 'calendar','point_of_sale'],
    'images':[
        'static/description/1.jpg',
        'static/description/2.jpg',
        'static/description/3.jpg',
        'static/src/img/icons8breakfast64.png'
    ],
    'installable': True,
    'qweb': [
        # 'static/src/xml/*.xml',
        'static/src/xml/Chrome.xml',
        'static/src/xml/ReservationButton.xml',
        'static/src/xml/TicketScreen/TicketScreen.xml',
        'static/src/xml/ReservationDetails/ReservationDetailsEdit.xml',
        'static/src/xml/website_calendar_booking_modal1.xml'

             ],
}
