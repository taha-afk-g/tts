<?php
// process_order.php

// Step 1: Get form data from POST request
$firstName = isset($_POST['first-name']) ? htmlspecialchars(trim($_POST['first-name'])) : '';
$lastName = isset($_POST['last-name']) ? htmlspecialchars(trim($_POST['last-name'])) : '';
$address1 = isset($_POST['address1']) ? htmlspecialchars(trim($_POST['address1'])) : '';
$address2 = isset($_POST['address2']) ? htmlspecialchars(trim($_POST['address2'])) : '';
$city = isset($_POST['city']) ? htmlspecialchars(trim($_POST['city'])) : '';
$phone = isset($_POST['phone']) ? htmlspecialchars(trim($_POST['phone'])) : '';
$email = isset($_POST['email']) ? htmlspecialchars(trim($_POST['email'])) : '';

$deliveryCharges = 4.00;

// Step 2: Validate the data
$errors = [];

if (empty($firstName)) {
    $errors[] = 'First Name is required';
}

if (empty($lastName)) {
    $errors[] = 'Last Name is required';
}

if (empty($address1)) {
    $errors[] = 'Address Line 1 is required';
}

if (empty($city)) {
    $errors[] = 'City is required';
}

if (empty($phone)) {
    $errors[] = 'Phone number is required';
}

if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'Valid email is required';
}

// If there are errors, stop processing and show the errors
if (!empty($errors)) {
    echo '<h3>Please fix the following errors:</h3>';
    echo '<ul>';
    foreach ($errors as $error) {
        echo "<li>$error</li>";
    }
    echo '</ul>';
    exit();
}

// Step 3: Calculate the total cost from the cart (retrieved from localStorage)
$cart = isset($_POST['cart']) ? json_decode($_POST['cart'], true) : [];
$subtotal = 0.00;

foreach ($cart as $item) {
    $subtotal += $item['price'] * $item['quantity'];
}

$total = $subtotal + $deliveryCharges;

// Step 4: Process the order (this could involve saving to a database or sending a confirmation email)

// Example: Saving the order to a text file (replace this with database logic if needed)
$orderDetails = "Order from $firstName $lastName\n";
$orderDetails .= "Address: $address1, $address2, $city\n";
$orderDetails .= "Phone: $phone\n";
$orderDetails .= "Email: $email\n";
$orderDetails .= "Subtotal: $$subtotal\n";
$orderDetails .= "Delivery Charges: $$deliveryCharges\n";
$orderDetails .= "Total: $$total\n\n";

$orderDetails .= "Items:\n";
foreach ($cart as $item) {
    $orderDetails .= "- {$item['name']} x {$item['quantity']} @ \${$item['price']} each\n";
}

$file = 'orders.txt';  // You can store orders in a file, or ideally use a database
file_put_contents($file, $orderDetails, FILE_APPEND);

// Step 5: Send an email confirmation to the user (optional, using PHPMailer or PHP's mail function)
$to = $email;
$subject = "Order Confirmation from CocoNutzLB";
$message = "Dear $firstName $lastName,\n\n";
$message .= "Thank you for your order!\n";
$message .= "Here are the details of your order:\n\n";
$message .= $orderDetails;
$headers = "From: orders@coconutzlb.com";

// Use PHP's mail() function (you may replace this with PHPMailer for more robust emailing)
if (mail($to, $subject, $message, $headers)) {
    echo 'Order confirmation sent to your email.';
} else {
    echo 'Failed to send order confirmation email.';
}

// Step 6: Show a success message
echo "<h3>Order completed successfully!</h3>";
echo "<p>Your order has been placed. You will receive an order confirmation email shortly.</p>";
echo "<p>Total Amount Charged: $$total</p>";
