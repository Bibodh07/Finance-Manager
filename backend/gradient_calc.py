
# Function with two parameters: w and b

def function(w, b, x, y):
    return (w * x + b - y) ** 2


# Calculate partial derivatives
def gradient(w, b, x, y):
    error = w * x + b - y

    dw = 2 * x * error
    db = 2 * error

    return dw, db


# Initial parameters
w = 2.0
b = 1.0

# Training data
x = 3
y = 10

# Calculate gradient
dw, db = gradient(w, b, x, y)

print("Function value:", function(w, b, x, y))
print("Gradient with respect to w:", dw)
print("Gradient with respect to b:", db)
