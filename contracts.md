# Paymentus Clone - API Contracts & Integration Plan

## Frontend Components Completed
- ✅ Header with navigation and authentication
- ✅ Hero section with gradient background and network pattern
- ✅ Services section with stats and feature cards  
- ✅ Footer with quick links and contact info
- ✅ Payment Dashboard with tabs (Overview, Bills, History, Methods)
- ✅ Login/Registration modal with mock authentication
- ✅ Pay Bill modal with biller selection and payment flow

## Mock Data Currently Used (to be replaced with backend)
- `navigationItems` - Menu structure for header
- `heroContent` - Hero section text content
- `servicesData` - Service descriptions and features
- `statsData` - Company metrics (2,500+ billers, 597M+ payments, etc.)
- `mockUsers` - Demo user accounts for authentication
- `mockBills` - User bills with amounts, due dates, status
- `mockTransactions` - Payment history and confirmations
- `paymentMethods` - Saved payment methods per user
- `dashboardMetrics` - Dashboard statistics

## Required Backend API Endpoints

### Authentication Endpoints
```
POST /api/auth/login
- Body: { email, password }
- Response: { user, token }

POST /api/auth/register  
- Body: { email, password, name, phone }
- Response: { user, token }

POST /api/auth/logout
- Headers: Authorization: Bearer {token}
- Response: { success: true }

GET /api/auth/me
- Headers: Authorization: Bearer {token}
- Response: { user }
```

### User Management
```
GET /api/users/{userId}
PUT /api/users/{userId}
- Body: { name, phone, address }
```

### Bills Management
```
GET /api/bills?userId={userId}
- Response: [{ id, billerName, amount, dueDate, status, description }]

POST /api/bills
- Body: { userId, billerName, accountNumber, amount, dueDate }

PUT /api/bills/{billId}
- Body: { status, amount, dueDate }

DELETE /api/bills/{billId}
```

### Payment Processing
```
POST /api/payments/process
- Body: { billId, paymentMethodId, amount }
- Response: { transactionId, confirmationNumber, status }

GET /api/payments/history?userId={userId}
- Response: [{ id, amount, date, biller, method, status, confirmationNumber }]
```

### Payment Methods
```
GET /api/payment-methods?userId={userId}
POST /api/payment-methods
- Body: { userId, type, details, isDefault }

PUT /api/payment-methods/{methodId}
DELETE /api/payment-methods/{methodId}
```

### Dashboard Analytics
```
GET /api/dashboard/metrics?userId={userId}
- Response: { totalDue, nextDueDate, monthlyTotal, methodCount }
```

## Database Collections

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  name: String,
  phone: String,
  address: String,
  createdAt: Date,
  updatedAt: Date
}
```

### Bills Collection  
```javascript
{
  _id: ObjectId,
  userId: ObjectId,
  billerName: String,
  accountNumber: String,
  amount: Number,
  dueDate: Date,
  status: String (pending/paid/overdue),
  billType: String (utility/telecom/insurance/government),
  description: String,
  createdAt: Date,
  updatedAt: Date
}
```

### Transactions Collection
```javascript
{
  _id: ObjectId,
  userId: ObjectId,
  billId: ObjectId,
  amount: Number,
  paymentMethodId: ObjectId,
  confirmationNumber: String,
  status: String (processing/completed/failed),
  timestamp: Date,
  createdAt: Date
}
```

### PaymentMethods Collection
```javascript
{
  _id: ObjectId,
  userId: ObjectId,
  type: String (credit_card/bank_account/paypal),
  last4: String,
  brand: String,
  expiryMonth: Number,
  expiryYear: Number,
  bankName: String,
  accountType: String,
  email: String,
  isDefault: Boolean,
  createdAt: Date
}
```

## Frontend Integration Changes Required

1. **Replace Mock Data**: Remove hardcoded mock data and implement API calls
2. **Authentication Context**: Add React context for user state management
3. **API Client**: Create axios-based API client with error handling
4. **Loading States**: Add loading indicators for async operations
5. **Error Handling**: Add proper error messages and validation
6. **Real Payment Flow**: Implement actual payment processing logic

## Security Considerations

- JWT token authentication
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting for API endpoints
- CORS configuration
- Environment variables for sensitive data

## Testing Strategy

- Backend API endpoints with mock data
- Frontend authentication flow
- Payment processing workflow
- Dashboard functionality
- Error scenarios and edge cases