import pandas as pd
from datetime import datetime
import sqlite3
from sqlite3 import IntegrityError
from django.core.management.base import BaseCommand, CommandError
from RMS_api.models import BusinessHours, Store, StoreStatus
# disable warnings about timezone
import warnings
warnings.filterwarnings(
    "ignore", message="DateTimeField .* received a naive datetime")

conn = sqlite3.connect('db.sqlite3')


class Command(BaseCommand):
    help = 'Import data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('businesshours_file', type=str,
                            help='Path to BusinessHours CSV file')
        parser.add_argument('status_file', type=str,
                            help='Path to StoreStatus CSV file')
        parser.add_argument('timezone_file', type=str,
                            help='Path to StoreTimezone CSV file')

    def handle(self, *args, **options):

        # Read StoreTimezone CSV file and dump to sql table
        # Initialize database
        with open(options['timezone_file'], 'r') as f:
            df = pd.read_csv(f)
            # skip header row
            df = df.iloc[1:]
            # dump csv to sql table
            df.to_sql('RMS_api_store', con=conn,
                      if_exists='replace', index=False)
        # Read BusinessHours CSV file and dump to sql table
        with open(options['businesshours_file'], 'r') as f:
            df = pd.read_csv(f)
            # skip header row
            df = df.iloc[1:]
            # dump csv to sql table
            df.to_sql('RMS_api_businesshours', con=conn,
                      if_exists='replace', index=False)
        # Read StoreStatus CSV file and dump to sql table
        with open(options['status_file'], 'r') as f:
            df = pd.read_csv(f)
            # skip header row
            df = df.iloc[1:]
            # dump csv to sql table
            df.to_sql('RMS_api_storestatus', con=conn,
                      if_exists='replace', index=False)

        # Read BusinessHours CSV file
        # with open(options['businesshours_file'], 'r') as f:
        #     reader = csv.reader(f)
        #     next(reader)  # skip header row
        #     for row in reader:
        #         store_id = row[0]
        #         try:
        #             store = Store.objects.get(store_id=store_id)
        #         except Store.DoesNotExist:
        #             # Handle the case where the store does not exist
        #             continue
        #         day_of_week = int(row[1])
        #         start_time_local = datetime.strptime(row[2], '%H:%M:%S').time()
        #         end_time_local = datetime.strptime(row[3], '%H:%M:%S').time()
        #         try:
        #             BusinessHours.objects.create(store=store, day_of_week=day_of_week,
        #                                          start_time_local=start_time_local, end_time_local=end_time_local)
        #         except IntegrityError:
        #             # Handle the case where the record already exists
        #             continue

        # Read StoreStatus CSV file
        # with open(options['status_file'], 'r') as f:
        #     reader = pd.read_csv(f)
        #     next(reader)  # skip header row
        #     for row in reader:
        #         store_id = row[0]
        #         try:
        #             store = Store.objects.get(store_id=store_id)
        #         except Store.DoesNotExist:
        #             # Handle the case where the store does not exist
        #             continue
        #         status = row[1]
        #         # remove microseconds and "UTC" suffix
        #         timestamp_str = row[2].split('.')[0]
        #         timestamp_utc = datetime.strptime(
        #             timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)
        #         try:
        #             StoreStatus.objects.create(
        #                 store=store, timestamp_utc=timestamp_utc, status=status)
        #         except IntegrityError:
        #             # Handle the case where the record already exists
        #             continue

        # # Load CSV data into a pandas DataFrame
        # df = pd.read_csv(options['status_file'])
        # # Convert timestamp_utc column to datetime
        # df['timestamp_utc'] = pd.to_datetime(
        #     df['timestamp_utc'].str.split('.').str[0], format='mixed')
        # rows_processed = 0
        # # Iterate over rows and create StoreStatus objects
        # for _, row in df.iterrows():
        #     rows_processed += 1
        #     if rows_processed % 1000 == 0:
        #         print(f"Processed {rows_processed} rows")
        #     try:
        #         store = Store.objects.get(store_id=row['store_id'])
        #     except Store.DoesNotExist:
        #         # Handle the case where the store does not exist
        #         continue
        #     try:
        #         StoreStatus.objects.create(
        #             store=store, timestamp_utc=row['timestamp_utc'], status=row['status'])
        #     except IntegrityError:
        #         # Handle the case where the record already exists
        #         continue
        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))
