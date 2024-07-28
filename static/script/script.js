document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');

    app.innerHTML =
        <form id="userForm">
            <h2>Create User</h2>
            <input type="email" id="email" placeholder="Email" required>
            <input type="text" id="name" placeholder="Name" required>
            <input type="text" id="mobile_number" placeholder="Mobile Number" required>
            <button type="submit">Create User</button>
        </form>
    ;

    document.getElementById('userForm').addEventListener('submit', async (event) => {
        event.preventDefault();
        const email = document.getElementById('email').value;
        const name = document.getElementById('name').value;
        const mobile_number = document.getElementById('mobile_number').value;

        const response = await fetch('/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, name, mobile_number })
        });

        const result = await response.json();
        alert(result.message);
    });
});