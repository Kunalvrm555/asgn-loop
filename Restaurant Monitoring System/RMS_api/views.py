from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import datetime, timedelta
from pytz import timezone

from .models import Store, StoreStatus, BusinessHours
from .serializers import ReportSerializer


class TriggerReportView(APIView):
    def get(self, request):
        report_id = generate_report()
        return Response({'report_id': report_id}, status=status.HTTP_200_OK)


class GetReportView(APIView):
    def get(self, request):
        report_id = request.query_params.get('report_id')
        try:
            report_file = get_report(report_id)
            with open(report_file, 'r') as f:
                return Response(f.read(), content_type='text/csv')
        except ObjectDoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_report():
    # Get all stores
    stores = Store.objects.all()
    report_data = []

    # Get current timestamp
    current_time = datetime.utcnow()

    # Loop over all stores and generate report for each one
    for store in stores:
        # Get store's timezone
        timezone_str = store.timezone_str
        tz = timezone(timezone_str)

        # Get store's business hours
        business_hours = BusinessHours.objects.filter(store=store)
        if not business_hours.exists():
            # Assume store is open 24*7 if business hours are not defined
            uptime_last_hour = 60
            uptime_last_day = 24
            update_last_week = 24 * 7
            downtime_last_hour = 0
            downtime_last_day = 0
            downtime_last_week = 0
            report_data.append({
                'store_id': store.id,
                'uptime_last_hour': uptime_last_hour,
                'uptime_last_day': uptime_last_day,
                'update_last_week': update_last_week,
                'downtime_last_hour': downtime_last_hour,
                'downtime_last_day': downtime_last_day,
                'downtime_last_week': downtime_last_week
            })
            continue

        # Get store's latest status within the last hour
        latest_status = StoreStatus.objects.filter(
            store=store, timestamp_utc__gte=current_time-timedelta(hours=1)).order_by('-timestamp_utc').first()
        if latest_status is None:
            # Assume store was inactive in the last hour if there is no latest status
            latest_status = StoreStatus(
                store=store, timestamp_utc=current_time-timedelta(minutes=30), status='inactive')

        # Get all store statuses within the last day
        statuses_last_day = StoreStatus.objects.filter(
            store=store, timestamp_utc__gte=current_time-timedelta(days=1))

        # Initialize report data
        uptime_last_hour = 0
        downtime_last_hour = 0
        uptime_last_day = 0
        downtime_last_day = 0
        update_last_week = 0

        # Loop over each day of the week and calculate uptime and downtime
        for day_of_week in range(7):
            # Get store's business hours for the current day
            business_hours_today = business_hours.filter(
                day_of_week=day_of_week)
            if not business_hours_today.exists():
                # Assume store is closed if business hours are not defined for the current day
                continue

            # Get start and end time
            start_time_local = business_hours_today.first().start_time_local
            end_time_local = business_hours_today.first().end_time_local

            # Convert start and end time to UTC
            start_time_utc = tz.localize(datetime.combine(
                datetime.utcnow().date(), start_time_local)).astimezone(timezone('UTC'))
            end_time_utc = tz.localize(datetime.combine(
                datetime.utcnow().date(), end_time_local)).astimezone(timezone('UTC'))

            # Get store statuses within the current day
            statuses_today = statuses_last_day.filter(
                timestamp_utc__gte=start_time_utc, timestamp_utc__lte=end_time_utc)

            # Calculate uptime and downtime for the current day
            uptime_today = 0
            downtime_today = 0
            for status in statuses_today:
                if status.status == 'active':
                    uptime_today += 1
                else:
                    downtime_today += 1

            # Calculate uptime and downtime for the last hour
            if latest_status.timestamp_utc >= start_time_utc and latest_status.timestamp_utc <= end_time_utc:
                if latest_status.status == 'active':
                    uptime_last_hour += 1
                else:
                    downtime_last_hour += 1

            # Calculate uptime and downtime for the last day
            uptime_last_day += uptime_today
            downtime_last_day += downtime_today

            # Calculate uptime for the last week
            if day_of_week == current_time.weekday():
                update_last_week += uptime_today

        # Calculate downtime for the last week
        downtime_last_week = 24 * 7 - update_last_week

        # Add report data to the list
        report_data.append({
            'store_id': store.id,
            'uptime_last_hour': uptime_last_hour,
            'uptime_last_day': uptime_last_day,
            'update_last_week': update_last_week,
            'downtime_last_hour': downtime_last_hour,
            'downtime_last_day': downtime_last_day,
            'downtime_last_week': downtime_last_week

        })

    # Generate report file
    report_file = 'report.csv'
    with open(report_file, 'w') as f:
        serializer = ReportSerializer(report_data, many=True)
        f.write(serializer.data)
        f.close()

