# Vox Pop

- Using a convention of /meeting-name/user-name, allow users to "queue up" to speak.
- Admin interface exists at /meeting-name/admin, which will allow removing users, and toggling them in and out of the speaking queue.
- Meetings expire after 90 minutes of inactivity (to free up the meeting name for the next meeting)
- Single-page Vue app, with Flask + SocketIO powering the API
