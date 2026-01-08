"""ICS file generation service for meeting calendar events."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from icalendar import Calendar, Event
from sqlalchemy.orm import Session

from app.db.models import Meeting


def generate_ics_file(meeting: Meeting) -> str:
    """Generate .ics file content for a meeting.
    
    Args:
        meeting: Meeting model instance
        
    Returns:
        ICS file content as string
    """
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//CreditNexus//Meeting Calendar//EN')
    cal.add('version', '2.0')
    
    # Create event
    event = Event()
    event.add('summary', meeting.title)
    event.add('description', meeting.description or '')
    event.add('dtstart', meeting.scheduled_at)
    event.add('dtend', meeting.scheduled_at + timedelta(minutes=meeting.duration_minutes))
    event.add('dtstamp', datetime.utcnow())
    event.add('uid', f'meeting-{meeting.id}@creditnexus.com')
    
    # Add location (meeting link or virtual)
    if meeting.meeting_link:
        event.add('location', meeting.meeting_link)
    else:
        event.add('location', 'Virtual Meeting')
    
    # Add organizer
    if meeting.organizer and hasattr(meeting.organizer, 'email'):
        event.add('organizer', meeting.organizer.email)
    
    # Add attendees
    if meeting.attendees:
        for attendee in meeting.attendees:
            if isinstance(attendee, dict):
                email = attendee.get('email', '')
                name = attendee.get('name', '')
                if email:
                    event.add('attendee', f'MAILTO:{email}', parameters={'CN': name})
    
    # Add to calendar
    cal.add_component(event)
    
    # Serialize to string
    return cal.to_ical().decode('utf-8')


def save_ics_file(meeting: Meeting, db: Session, content: Optional[str] = None) -> str:
    """Save .ics file to disk and update meeting record.
    
    Args:
        meeting: Meeting model instance
        db: Database session
        content: ICS file content (if None, will generate)
        
    Returns:
        File path to saved .ics file
    """
    # Generate content if not provided
    if content is None:
        content = generate_ics_file(meeting)
    
    # Create storage directory
    storage_dir = Path('storage/meetings')
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate file path
    file_path = storage_dir / f'meeting_{meeting.id}.ics'
    
    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update meeting record
    meeting.ics_file_path = str(file_path)
    db.commit()
    
    return str(file_path)


def get_ics_file_path(meeting: Meeting) -> Optional[str]:
    """Get the file path for a meeting's .ics file.
    
    Args:
        meeting: Meeting model instance
        
    Returns:
        File path if exists, None otherwise
    """
    if not meeting.ics_file_path:
        return None
    
    path = Path(meeting.ics_file_path)
    if path.exists():
        return str(path)
    
    return None
