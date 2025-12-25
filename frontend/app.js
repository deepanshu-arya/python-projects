async function createBill() {

    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;
    const items = document.getElementById("items").value;

    const response = await fetch("http://127.0.0.1:8000/create-transaction", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            customer_name: name,
            phone: phone,
            items_text: items
        })
    });

    const data = await response.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}
