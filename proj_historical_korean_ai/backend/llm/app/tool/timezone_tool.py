from datetime import timezone, timedelta

KST = timezone(timedelta(hours=9))

class TimezoneTool:

    @staticmethod
    def format_to_kst_str(dt):
        if not dt:
            return None
        
        if dt.tzinfo is None:
            print("1")
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S")