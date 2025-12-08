from django.utils.deprecation import MiddlewareMixin
import re
from django.utils import timezone
from datetime import timedelta

class DisableXFrameOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']
        return response



class VisitorTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track website visitors.
    Tracks IP, path, user agent, and other visitor information.
    """
    
    # Paths to exclude from tracking (admin, static files, etc.)
    EXCLUDE_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/apps/static/',
        '/apps/media/',
    ]
    
    # File extensions to exclude (static files, images, etc.)
    EXCLUDE_EXTENSIONS = [
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot', '.otf',  # Fonts
        '.pdf', '.zip', '.rar', '.tar', '.gz',  # Archives
        '.mp4', '.mp3', '.avi', '.mov', '.wmv',  # Media files
        '.xml', '.json', '.txt', '.csv',  # Data files
        '.map',  # Source maps
    ]
    
    def process_request(self, request):
        """Track visitor on each request"""
        path = request.path.lower()
        
        # Skip tracking for excluded paths
        if any(path.startswith(exclude_path.lower()) for exclude_path in self.EXCLUDE_PATHS):
            return None
        
        # Skip tracking for files with excluded extensions
        if any(path.endswith(ext) for ext in self.EXCLUDE_EXTENSIONS):
            return None
        
        # Skip tracking for paths containing static/media keywords (like /apps/static/)
        if '/static/' in path or '/media/' in path or '/assets/' in path:
            return None
        
        # Skip tracking for AJAX requests (optional - you can remove this if you want to track AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return None
        
        try:
            from apps.home.models import Visitor
            
            # Get IP address
            ip_address = self.get_client_ip(request)
            
            # Check if we should track this visit (avoid duplicate tracking in same session)
            # Only track once per session per path to avoid spam
            session_key = request.session.session_key
            if session_key:
                # Check if we already tracked this path in this session recently (within 5 minutes)
                five_minutes_ago = timezone.now() - timedelta(minutes=5)
                recent_visit = Visitor.objects.filter(
                    session_key=session_key,
                    path=request.path,
                    visited_at__gte=five_minutes_ago
                ).exists()
                
                if recent_visit:
                    return None  # Skip tracking duplicate visit
            
            # Parse user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            browser, os, device_type = self.parse_user_agent(user_agent)
            
            # Get referer
            referer = request.META.get('HTTP_REFERER', '')
            
            # Build full path
            full_path = request.build_absolute_uri()
            
            # Create visitor record
            Visitor.objects.create(
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else None,  # Limit length
                referer=referer[:500] if referer else None,
                path=request.path[:500],
                full_path=full_path[:500],
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                browser=browser,
                os=os,
                device_type=device_type,
            )
            
        except Exception as e:
            # Log error but don't break the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error tracking visitor: {str(e)}")
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def parse_user_agent(self, user_agent):
        """Parse user agent string to extract browser, OS, and device type"""
        if not user_agent:
            return None, None, None
        
        browser = None
        os = None
        device_type = None
        
        user_agent_lower = user_agent.lower()
        
        # Detect browser
        if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
            browser = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser = 'Firefox'
        elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            browser = 'Safari'
        elif 'edg' in user_agent_lower:
            browser = 'Edge'
        elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
            browser = 'Opera'
        else:
            browser = 'Other'
        
        # Detect OS
        if 'windows' in user_agent_lower:
            os = 'Windows'
        elif 'mac' in user_agent_lower or 'macintosh' in user_agent_lower:
            os = 'macOS'
        elif 'linux' in user_agent_lower:
            os = 'Linux'
        elif 'android' in user_agent_lower:
            os = 'Android'
        elif 'ios' in user_agent_lower or 'iphone' in user_agent_lower or 'ipad' in user_agent_lower:
            os = 'iOS'
        else:
            os = 'Other'
        
        # Detect device type
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower:
            device_type = 'Mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            device_type = 'Tablet'
        else:
            device_type = 'Desktop'
        
        return browser, os, device_type
