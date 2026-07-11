// KidGuard WebSocket Client

document.addEventListener('DOMContentLoaded', function () {

    // Check login
    const isLoggedIn =
        document.body.classList.contains('logged-in') ||
        document.querySelector('[data-user-id]') !== null;

    if (!isLoggedIn) {
        console.log('WebSocket not initialized: User not logged in');
        return;
    }

    // Request notification permission
    requestNotificationPermission();

    // Initialize socket
    const socket = io();

    socket.on('connect', function () {

        console.log('WebSocket connected');

        const userElement = document.querySelector('[data-user-id]');
        const userId = userElement
            ? userElement.getAttribute('data-user-id')
            : null;

        if (userId) {

            socket.emit('join', {
                room: userId
            });

            console.log('Joined room:', userId);
        }
    });

    socket.on('disconnect', function () {
        console.log('WebSocket disconnected');
    });

    socket.on('new_alert', function (data) {

        console.log('New alert received:', data);

        showNotification(data);

        updateAlertUI(data);

        playAlertSound(data.alert_type);
    });

    socket.on('error', function (error) {
        console.error('WebSocket error:', error);
    });

});


// Request browser notification permission
function requestNotificationPermission() {

    if ('Notification' in window) {

        if (
            Notification.permission !== 'granted' &&
            Notification.permission !== 'denied'
        ) {

            Notification.requestPermission().then(function (permission) {
                console.log('Notification permission:', permission);
            });

        }
    }
}


// Show notification
function showNotification(alertData) {

    if (
        !('Notification' in window) ||
        Notification.permission !== 'granted'
    ) {
        return;
    }

    let title;
    let options;

    switch (alertData.alert_type) {

        case 'emergency':

            title = 'EMERGENCY ALERT';

            options = {
                body:
                    alertData.child_name +
                    ': ' +
                    (alertData.message || 'Emergency assistance needed!'),

                icon: '/static/img/emergency-icon.png',

                requireInteraction: true,

                vibrate: [200, 100, 200]
            };

            break;

        case 'inappropriate_content':

            title = 'Content Alert';

            options = {
                body:
                    alertData.child_name +
                    ': ' +
                    alertData.message,

                icon: '/static/img/warning-icon.png'
            };

            break;

        default:

            title = 'KidGuard Alert';

            options = {
                body: alertData.message,
                icon: '/static/img/notification-icon.png'
            };
    }

    const notification = new Notification(title, options);

    notification.onclick = function () {

        window.focus();

        if (alertData.alert_id) {
            window.location.href = '/alert/' + alertData.alert_id;
        }
    };
}


// Update alert UI
function updateAlertUI(alertData) {

    const alertsContainer =
        document.querySelector('.alerts-container');

    if (!alertsContainer) return;

    const alertElement = document.createElement('div');

    alertElement.classList.add('alert-item', 'unread');

    alertElement.setAttribute(
        'data-alert-id',
        alertData.alert_id
    );

    let iconClass;

    switch (alertData.alert_type) {

        case 'emergency':
            iconClass = 'fa-exclamation-triangle text-danger';
            break;

        case 'inappropriate_content':
            iconClass = 'fa-exclamation-circle text-warning';
            break;

        default:
            iconClass = 'fa-info-circle text-info';
    }

    alertElement.innerHTML = `
        <div class="d-flex">
            <div class="me-3">
                <i class="fas ${iconClass} fa-lg"></i>
            </div>

            <div>
                <div class="alert-message">
                    ${alertData.message}
                </div>

                <div class="alert-meta">
                    <span class="alert-from">
                        ${alertData.child_name}
                    </span>

                    <span class="alert-time">
                        ${alertData.timestamp}
                    </span>
                </div>
            </div>
        </div>
    `;

    alertElement.addEventListener('click', function () {

        window.location.href =
            '/alert/' + alertData.alert_id;
    });

    alertsContainer.prepend(alertElement);

    const alertBadge =
        document.querySelector('.alert-badge');

    if (alertBadge) {

        const currentCount =
            parseInt(alertBadge.textContent) || 0;

        alertBadge.textContent = currentCount + 1;

        alertBadge.style.display = 'block';
    }
}


// Play alert sound
function playAlertSound(alertType) {

    let soundUrl;

    switch (alertType) {

        case 'emergency':

            soundUrl =
                'https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3';

            break;

        case 'inappropriate_content':

            soundUrl =
                'https://assets.mixkit.co/sfx/preview/mixkit-alert-quick-chime-766.mp3';

            break;

        default:

            soundUrl =
                'https://assets.mixkit.co/sfx/preview/mixkit-positive-notification-951.mp3';
    }

    const audio = new Audio(soundUrl);

    audio.play().catch(function (error) {

        console.warn('Audio playback failed:', error);
    });
}