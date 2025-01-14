
// Modal and UI Control Functions
// Admin Dashboard
        function closeAllModals() {
            document.getElementById('modal-overlay').classList.remove('show');
            document.getElementById('add-plan-modal').classList.remove('show');
            document.getElementById('add-competition-modal').classList.remove('show');
            document.querySelectorAll('.edit-form').forEach(form => {
                form.classList.remove('show');
            });
            document.querySelectorAll('.card-detailed').forEach(detailed => {
                detailed.classList.remove('show');
            });
        }

        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert ${type}`;
            alert.style.display = 'block';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 3000);
        }

        function closeEditForm(element) {
            element.closest('.edit-form').classList.remove('show');
        }

        function closeDetailed(element) {
            element.closest('.card-detailed').classList.remove('show');
        }

        // CRUD Operations
        async function handleDelete(itemId, section) {
            if (confirm('Are you sure you want to delete this item?')) {
                try {
                    const response = await fetch(`/admin/${section}/delete/${itemId}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        showAlert('Item deleted successfully', 'success');
                        // Remove the card from the UI
                        const card = document.querySelector(`.card[data-id="${itemId}"]`);
                        if (card) {
                            const section = card.closest('.section');
                            card.remove();

                            // Check if there are any remaining cards
                            const remainingCards = section.querySelectorAll('.card:not(.empty)');

                            if (remainingCards.length === 0) {
                                // Add empty card if no cards remain
                                const emptyCard = document.createElement('div');
                                emptyCard.className = 'card empty';
                                emptyCard.innerHTML = `<p>No ${section.id} available</p>`;
                                section.querySelector('.scroll-container').appendChild(emptyCard);
                            }
                        }
                    } else {
                        showAlert(data.message || 'Failed to delete item', 'error');
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    showAlert('An error occurred while deleting the item', 'error');
                }
            }
        }

        async function handleEdit(element, type) {
            const form = element.closest('form');
            const card = element.closest('.card');
            const formData = new FormData(form);
            const itemId = card.dataset.id;

            try {
                const response = await fetch(`/admin/${type}/edit/${itemId}`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    showAlert('Item updated successfully', 'success');
                    location.reload();
                } else {
                    showAlert(data.message || 'Failed to update item', 'error');
                }
            } catch (error) {
                showAlert('An error occurred while updating the item', 'error');
            }
        }

        // HTML Generation Functions
        function generatePlanCardHTML(plan) {
            return `
                <div class="card" data-id="${plan.training_plan_id}">
                    <div class="card-controls">
                        <button class="card-button delete">×</button>
                    </div>
                    <div class="card-content">
                        <div class="card-initial">${plan.plan_name[0]}</div>
                        <div class="card-details">
                            <p>${plan.plan_name}</p>
                            <small>₱${plan.monthly_fee}/month</small>
                            <small>₱${plan.weekly_fee}/week</small>
                            <small>₱${plan.private_hourly_fee}/hour</small>
                        </div>
                    </div>
                    <div class="card-detailed">
                        <button class="close-button" onclick="closeDetailed(this)">×</button>
                        <h3>${plan.plan_name}</h3>
                        <p>Monthly Fee: ₱${plan.monthly_fee}</p>
                        <p>Weekly Fee: ₱${plan.weekly_fee}</p>
                        <p>Private Hour: ₱${plan.private_hourly_fee}</p>
                    </div>
                    <form class="edit-form">
                        <label>Plan Name:</label>
                        <input type="text" name="plan_name" value="${plan.plan_name}">
                        <label>Monthly Fee:</label>
                        <input type="number" name="monthly_fee" value="${plan.monthly_fee}">
                        <label>Weekly Fee:</label>
                        <input type="number" name="weekly_fee" value="${plan.weekly_fee}">
                        <label>Private Hour Fee:</label>
                        <input type="number" name="private_hourly_fee" value="${plan.private_hourly_fee}">
                        <div class="edit-form-buttons">
                            <button type="button" class="cancel" onclick="closeEditForm(this)">Cancel</button>
                            <button type="button" class="save" onclick="handleEdit(this, 'plans')">Save</button>
                        </div>
                    </form>
                </div>
            `;
        }

        function generateCompetitionCardHTML(competition) {
            return `
                <div class="card" data-id="${competition.competition_id}">
                    <div class="card-controls">
                        <button class="card-button delete">×</button>
                    </div>
                    <div class="card-content">
                        <div class="card-initial">${competition.competition_name[0]}</div>
                        <div class="card-details">
                            <p>${competition.competition_name}</p>
                            <small>${competition.date}</small>
                        </div>
                    </div>
                    <div class="card-detailed">
                        <button class="close-button" onclick="closeDetailed(this)">×</button>
                        <h3>${competition.competition_name}</h3>
                        <p>Date: ${competition.date}</p>
                        <p>Location: ${competition.location}</p>
                        <p>Entry Fee: ₱${competition.entry_fee}</p>
                    </div>
                    <form class="edit-form">
                        <label>Competition Name:</label>
                        <input type="text" name="competition_name" value="${competition.competition_name}">
                        <label>Date:</label>
                        <input type="date" name="date" value="${competition.date}">
                        <label>Location:</label>
                        <input type="text" name="location" value="${competition.location}">
                        <label>Entry Fee:</label>
                        <input type="number" name="entry_fee" value="${competition.entry_fee}">
                        <div class="edit-form-buttons">
                            <button type="button" class="cancel" onclick="closeEditForm(this)">Cancel</button>
                            <button type="button" class="save" onclick="handleEdit(this, 'competitions')">Save</button>
                        </div>
                    </form>
                </div>
            `;
        }

        // Form Submission Handlers
        function initializeFormHandlers() {
            // Add Plan Form Handler
            document.getElementById('add-plan-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);

                try {
                    const response = await fetch('/admin/plans/add', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();

                    if (data.success) {
                        showAlert(data.message, 'success');
                        closeAllModals();
                        location.reload();
                    } else {
                        showAlert(data.message, 'error');
                    }
                } catch (error) {
                    showAlert('An error occurred while adding the plan', 'error');
                }
            });

            // Add Competition Form Handler
            document.getElementById('add-competition-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);

                try {
                    const response = await fetch('/admin/competitions/add', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();

                    if (data.success) {
                        showAlert(data.message, 'success');
                        closeAllModals();
                        location.reload();
                    } else {
                        showAlert(data.message, 'error');
                    }
                } catch (error) {
                    showAlert('An error occurred while adding the competition', 'error');
                }
            });
        }

        // Event Listeners Initialization
        function initializeEventListeners() {
            // Delete button listeners
            document.querySelectorAll('.card-button.delete').forEach(button => {
                button.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const card = button.closest('.card');
                    const itemId = card.dataset.id;
                    const section = card.closest('.section').id;
                    handleDelete(itemId, section);
                });
            });

            // Card content click listeners
            document.querySelectorAll('.card-content').forEach(content => {
                content.addEventListener('click', (e) => {
                    if (!e.target.closest('.card-controls')) {
                        const card = content.closest('.card');
                        const detailed = card.querySelector('.card-detailed');
                        if (detailed) {
                            detailed.classList.add('show');
                        }
                    }
                });
            });

            // Modal overlay click handler
            document.getElementById('modal-overlay').addEventListener('click', closeAllModals);
        }

        // Initialize everything when the DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            initializeFormHandlers();
            initializeEventListeners();
        });



// Competition Registration

function updatePaymentForm() {
    const paymentMethod = document.getElementById('payment_method').value;
    const cardDetails = document.getElementById('card_details');
    const paypalDetails = document.getElementById('paypal_details');
    const bankDetails = document.getElementById('bank_details');

    cardDetails.style.display = 'none';
    paypalDetails.style.display = 'none';
    bankDetails.style.display = 'none';

    if (paymentMethod === 'credit') {
        cardDetails.style.display = 'block';
    } else if (paymentMethod === 'paypal') {
        paypalDetails.style.display = 'block';
    } else if (paymentMethod === 'bank') {
        bankDetails.style.display = 'block';
    }
}

window.onload = updatePaymentForm;

// Main Dashboard

document.addEventListener('DOMContentLoaded', () => {

            const menuIcon = document.querySelector('.menu-icon');
            const dropdown = document.querySelector('.dropdown');

            menuIcon.addEventListener('click', () => {
                dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
            });

            document.addEventListener('click', (event) => {
                if (!menuIcon.contains(event.target) && !dropdown.contains(event.target)) {
                    dropdown.style.display = 'none';
                }
            });

            // Athletes section
            const athleteCards = document.querySelectorAll('#athletes .card');
            athleteCards.forEach(card => {
                card.onclick = function() {
                    const content = `
                        <strong>Age:</strong> ${this.getAttribute('data-age')}<br>
                        <strong>Weight:</strong> ${this.getAttribute('data-weight')} kg<br>
                        <strong>Weight Category:</strong> ${this.getAttribute('data-category')}<br>
                    `;
                    showDetails(`Athlete: ${this.getAttribute('data-name')}`, content);
                };
            });

            // Plans section
            const planCards = document.querySelectorAll('#plans .card');
            planCards.forEach(card => {
                card.onclick = function() {
                    const content = `
                        <strong>Description:</strong> ${this.getAttribute('data-description')}<br>
                        <strong>Monthly Fee:</strong> ₱${this.getAttribute('data-monthly-fee')}<br>
                        <strong>Weekly Fee:</strong> ₱${this.getAttribute('data-weekly-fee')}<br>
                        <strong>Private Hourly Fee:</strong> ₱${this.getAttribute('data-hourly-fee')}<br>
                        <strong>Category:</strong> ${this.getAttribute('data-category')}<br>
                        <strong>Sessions Per Week:</strong> ${this.getAttribute('data-sessions')}<br>
                        <button
                            class='modal-button'
                            data-athlete-id='${this.getAttribute('data-athlete-id')}'
                            data-plan-id='${this.getAttribute('data-plan-id')}'
                            onclick='registerForPlan(this); event.stopPropagation();'>
                            Register for Training plan
                        </button>
                    `;
                    showDetails(this.getAttribute('data-name'), content);
                };
            });


            // Competitions section
            const competitionCards = document.querySelectorAll('#competitions .card');
            competitionCards.forEach(card => {
                card.onclick = function() {
                    const registerUrl = this.getAttribute('data-register-url');
                    const content = `
                        <div class="competition-details">
                            <h3>${this.getAttribute('data-name')}</h3>
                            <p><strong>Location:</strong> ${this.getAttribute('data-location')}</p>
                            <p><strong>Date:</strong> ${this.getAttribute('data-date')}</p>
                            <p><strong>Competition Fee:</strong> ₱${this.getAttribute('data-entry-fee')}</p>
                            <p><strong>Category:</strong> ${this.getAttribute('data-category')}</p>
                            <button onclick="window.location.href='${registerUrl}'" class='modal-button'>
                                Register for Competition
                            </button>
                        </div>`;
                    showDetails('Competition Details', content);
                };
            });
        });

        function registerForPlan(button) {
            // Close any open modals first

            const athleteId = button.getAttribute('data-athlete-id');
            const trainingPlanId = button.getAttribute('data-plan-id');

            const form = document.createElement("form");
            form.method = "POST";
            form.action = `/payment_session_type/${athleteId}/${trainingPlanId}`;

            const sessionTypeField = document.createElement("input");
            sessionTypeField.type = "hidden";
            sessionTypeField.name = "session_type";
            sessionTypeField.value = "default_session";

            form.appendChild(sessionTypeField);
            document.body.appendChild(form);
            form.submit();
        }

        function showCompetitionDetails(card) {
            const registerUrl = card.dataset.registerUrl;
            const details = `
                <div class="competition-details">
                    <h3>${card.dataset.competitionName}</h3>
                    <p><strong>Location:</strong> ${card.dataset.location}</p>
                    <p><strong>Date:</strong> ${card.dataset.date}</p>
                    <p><strong>Competition Fee:</strong> ₱${card.dataset.entryFee}</p>
                    <p><strong>Category:</strong> ${card.dataset.category}</p>
                    <button onclick="registerForCompetition('${registerUrl}')" class="modal-close">
                        Register for Competition
                    </button>
                </div>`;

            showDetails(card.dataset.competitionName, details);
        }

        function registerForCompetition(url) {
            closeModal();  // Close modal before redirecting
            window.location.href = url;
        }


        // Add error handling to showDetails
        function showDetails(title, content) {
            try {
                const modalTitle = document.getElementById('modal-title');
                const modalContent = document.getElementById('modal-content');
                const modalOverlay = document.getElementById('modal-overlay');
                const modal = document.getElementById('modal');

                if (!modalTitle || !modalContent || !modalOverlay || !modal) {
                    console.error('Modal elements not found');
                    return;
                }

                modalTitle.textContent = title;
                modalContent.innerHTML = content; // Set content directly
                modalOverlay.style.display = 'block';
                modal.style.display = 'block';
            } catch (error) {
                console.error('Error showing modal:', error);
                closeModal();
            }
        }


        function scrollModal(direction) {
            const modal = document.getElementById('modal');
            const scrollAmount = 300; // Adjust scroll amount as needed

            if (direction === 'up') {
                modal.scrollBy({
                    top: -scrollAmount,
                    behavior: 'smooth'
                });
            } else {
                modal.scrollBy({
                    top: scrollAmount,
                    behavior: 'smooth'
                });
            }
        }

        function checkScrollButtons(modal) {
            const scrollButtons = modal.querySelector('.scroll-buttons');
            if (!scrollButtons) return;

            const hasScroll = modal.scrollHeight > modal.clientHeight;
            scrollButtons.classList.toggle('hidden', !hasScroll);

            // Position the buttons based on modal position
            const modalRect = modal.getBoundingClientRect();
            scrollButtons.style.top = `${modalRect.top + 20}px`;
            scrollButtons.style.height = `${modalRect.height - 40}px`; // Account for padding
        }


        function closeModal() {
            const modalElements = [
                'modal-overlay',
                'modal',
                'confirm-dialog'
            ];

            modalElements.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.style.display = 'none';
                }
            });

            // Also close any dynamically created overlays
            const extraOverlays = document.querySelectorAll('.modal-overlay');
            extraOverlays.forEach(overlay => {
                overlay.style.display = 'none';
            });
        }

        function cancelTraining(trainingId) {
            // Create form and submit directly
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/cancel_training/${trainingId}`;

            // Add CSRF token if needed
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfToken.content;
                form.appendChild(csrfInput);
            }

            // Append form to body and submit
            document.body.appendChild(form);
            form.submit();
        }

        function closeDialog() {
            const dialog = document.querySelector('.confirm-dialog');
            const overlay = document.querySelector('.modal-overlay');
            if (dialog) dialog.remove();
            if (overlay) overlay.remove();
        }

        function confirmCancelTraining(trainingId, dialog) {
            fetch(`/cancel_training/${trainingId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'  // Add this header
                },
                credentials: 'same-origin'  // Add this to ensure cookies are sent
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Remove the plan card from the display
                    const planCard = document.querySelector(`[data-training-id="${trainingId}"]`);
                    if (planCard) {
                        planCard.remove();
                    }

                    // Close the modal and refresh the athlete details
                    showAthleteDetails();  // Assuming this function will reload the athlete data
                    window.location.href = '/cancelTRaining'; // Redirect to cancelTRaining page
                } else {
                    throw new Error(data.message || 'Failed to cancel training plan');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to cancel training plan. Please try again.');
            })
            .finally(() => {
                closeDialog(dialog);
            });
        }



        function switchTab(tabName) {
            const tabs = document.querySelectorAll('.modal-tab');
            const sections = document.querySelectorAll('.modal-content-section');

            tabs.forEach(tab => {
                tab.classList.remove('active');
                if (tab.getAttribute('onclick').includes(tabName)) {
                    tab.classList.add('active');
                }
            });

            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === `${tabName}-section`) {
                    section.classList.add('active');
                }
            });
        }

        function showAthleteDetails() {
            closeModal()
            const athleteData = {
                name: "{{ athlete.name }}",
                age: {{ athlete.age }},
                current_weight: {{ athlete.current_weight }},
                weight_category: "{{ athlete.weight_category }}",
                athlete_id: "{{ athlete.athlete_id }}",
                trainings: [
                    {% for training in athlete.athlete_trainings %}
                    {
                        id: {{ training.id }},
                        plan_name: "{{ training.training_plan.plan_name }}",
                        start_date: "{{ training.start_date }}",
                        end_date: {% if training.end_date %}"{{ training.end_date }}"{% else %}null{% endif %},
                        category: "{{ training.training_plan.category }}",
                        session_per_week: {{ training.training_plan.session_per_week }}
                    }{% if not loop.last %},{% endif %}
                    {% endfor %}
                ],
                competitions: [
                    {% for comp in athlete.athlete_competitions %}
                    {
                        competition_name: "{{ comp.competition.competition_name }}",
                        date: "{{ comp.competition.date }}",
                        location: "{{ comp.competition.location }}",
                        weight_category: "{{ comp.competition.weight_category }}",
                        entry_fee: {{ comp.competition.entry_fee }},
                        registration_date: "{{ comp.registration_date }}"
                    }{% if not loop.last %},{% endif %}
                    {% endfor %}
                ]
            };

            const content = `
                <div class="athlete-section">
                    <h3>Profile Information</h3>
                    <p><strong>Name:</strong> ${athleteData.name}</p>
                    <p><strong>Age:</strong> ${athleteData.age}</p>
                    <p><strong>Weight:</strong> ${athleteData.current_weight} kg</p>
                    <p><strong>Category:</strong> ${athleteData.weight_category}</p>
                    <p><strong>Athlete ID:</strong> ${athleteData.athlete_id}</p>

                    <div class="athlete-subscriptions">
                        <h3>Active Training Plans</h3>
                        ${athleteData.trainings
                            .filter(training => !training.end_date)
                            .map(training => `
                                <div class="subscription-card">
                                    <h4>${training.plan_name}</h4>
                                    <p><strong>Started:</strong> ${training.start_date}</p>
                                    <p><strong>Category:</strong> ${training.category}</p>
                                    <p><strong>Sessions/Week:</strong> ${training.session_per_week}</p>
                                    <button
                                        class="cancel-button"
                                        onclick="cancelTraining(${training.id})">
                                        Cancel Training Plan
                                    </button>
                                </div>
                            `).join('')}
                    </div>

                    <div class="athlete-competitions">
                        <h3>Registered Competitions</h3>
                        ${athleteData.competitions.map(comp => `
                            <div class="competition-card">
                                <h4>${comp.competition_name}</h4>
                                <p><strong>Date:</strong> ${comp.date}</p>
                                <p><strong>Location:</strong> ${comp.location}</p>
                                <p><strong>Category:</strong> ${comp.weight_category}</p>
                                <p><strong>Entry Fee:</strong> ₱${comp.entry_fee}</p>
                                <p><strong>Registered:</strong> ${comp.registration_date}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>`;

            showDetails('Athlete Details', content);
        }

        function cancelTrainingHandler(trainingId) {
            cancelTraining(trainingId);
        }


        function showPaymentHistory() {
            const payments = [
                {% for payment in athlete.athlete_payments %}
                {
                    payment_date: "{{ payment.payment_date }}",
                    plan_name: "{{ payment.training_plan.plan_name }}",
                    plan_type: "{{ payment.plan_type }}",
                    amount: {{ payment.amount }},
                    payment_method: "{{ payment.payment_method }}"
                }{% if not loop.last %},{% endif %}
                {% endfor %}
            ];

            const trainings = [
                {% for training in athlete.athlete_trainings if not training.end_date %}
                {
                    id: {{ training.id }},
                    plan_name: "{{ training.training_plan.plan_name }}",
                    start_date: "{{ training.start_date }}",
                    category: "{{ training.training_plan.category }}",
                    monthly_fee: {{ training.training_plan.monthly_fee }},
                    weekly_fee: {% if training.training_plan.weekly_fee %}{{ training.training_plan.weekly_fee }}{% else %}null{% endif %},
                    private_hourly_fee: {% if training.training_plan.private_hourly_fee %}{{ training.training_plan.private_hourly_fee }}{% else %}null{% endif %}
                }{% if not loop.last %},{% endif %}
                {% endfor %}
            ];

            const content = `
                <div class="modal-tabs">
                    <button class="modal-tab active" onclick="switchTab('payments')">Payment History</button>
                    <button class="modal-tab" onclick="switchTab('subscriptions')">Active Plans</button>
                </div>
                <div id="payments-section" class="modal-content-section active">
                    <table class="payment-history">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Plan</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Payment Method</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${payments.map(payment => `
                                <tr>
                                    <td>${payment.payment_date}</td>
                                    <td>${payment.plan_name}</td>
                                    <td>${payment.plan_type}</td>
                                    <td>₱${payment.amount}</td>
                                    <td>${payment.payment_method}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div id="subscriptions-section" class="modal-content-section">
                    ${trainings.map(training => `
                        <div class="subscription-card">
                            <h3>${training.plan_name}</h3>
                            <p><strong>Started:</strong> ${training.start_date}</p>
                            <p><strong>Category:</strong> ${training.category}</p>
                            <p><strong>Monthly Fee:</strong> ₱${training.monthly_fee}</p>
                            ${training.weekly_fee ? `<p><strong>Weekly Fee:</strong> ₱${training.weekly_fee}</p>` : ''}
                            ${training.private_hourly_fee ? `<p><strong>Private Hour:</strong> ₱${training.private_hourly_fee}</p>` : ''}
                            <button
                                class="cancel-button"
                                onclick="cancelTraining(${training.id})">
                                Cancel Training Plan
                            </button>
                        </div>
                    `).join('')}
                </div>`;

            showDetails('Payments & Plans', content);
        }
}


// Guest View
document.addEventListener('DOMContentLoaded', () => {
            const menuIcon = document.querySelector('.menu-icon');
            const dropdown = document.querySelector('.dropdown');

            menuIcon.addEventListener('click', () => {
                dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
            });

            document.addEventListener('click', (event) => {
                if (!menuIcon.contains(event.target) && !dropdown.contains(event.target)) {
                    dropdown.style.display = 'none';
                }
            });
        });

        function showDetails(title, content) {
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-content').innerHTML = content;
            document.getElementById('modal-overlay').style.display = 'block';
            document.getElementById('modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('modal-overlay').style.display = 'none';
            document.getElementById('modal').style.display = 'none';
        }

        function showCompetitionDetails(card) {
            const details = `
                <div class="competition-details">
                    <h3>${card.dataset.competitionName}</h3>
                    <p><strong>Location:</strong> ${card.dataset.location}</p>
                    <p><strong>Date:</strong> ${card.dataset.date}</p>
                    <p><strong>Competition Fee:</strong> ₱${card.dataset.entryFee}</p>
                    <p><strong>Category:</strong> ${card.dataset.category}</p>
                    <p><em>Please log in to register for competitions.</em></p>
                </div>`;

            showDetails(card.dataset.competitionName, details);
        }

// Payment Mehtod

function updatePaymentForm() {
            const paymentMethod = document.getElementById('payment_method').value;
            const cardDetails = document.getElementById('card_details');
            const paypalDetails = document.getElementById('paypal_details');
            const bankDetails = document.getElementById('bank_details');

            // Hide all payment details by default
            cardDetails.style.display = 'none';
            paypalDetails.style.display = 'none';
            bankDetails.style.display = 'none';

            // Show payment details based on selected method
            if (paymentMethod === 'credit') {
                cardDetails.style.display = 'block';
            } else if (paymentMethod === 'paypal') {
                paypalDetails.style.display = 'block';
            } else if (paymentMethod === 'bank') {
                bankDetails.style.display = 'block';
            }
        }

// Payment Session
        document.getElementById('sessionForm').onsubmit = function(e) {
            const sessionType = document.getElementById('session_type').value;
            if (!sessionType) {
                e.preventDefault();
                alert('Please select a session type');
                return false;
            }
            return true;
        };

// Register
document.getElementById('registrationForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        try {
            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Display the athlete ID
                document.getElementById('athleteIdNumber').textContent = data.athlete_id;
                document.getElementById('athleteIdDisplay').classList.add('visible');

                // Clear the form
                e.target.reset();

                // Wait 3 seconds then redirect to login
                setTimeout(() => {
                    window.location.href = '/login';
                }, 3000);
            } else {
                // Handle error
                const notification = document.createElement('div');
                notification.className = 'notification error';
                notification.textContent = data.message || 'Registration failed. Please try again.';
                e.target.insertBefore(notification, e.target.firstChild);
            }
        } catch (error) {
            console.error('Error:', error);
            const notification = document.createElement('div');
            notification.className = 'notification error';
            notification.textContent = 'An error occurred. Please try again later.';
            e.target.insertBefore(notification, e.target.firstChild);
        }
    });

