// Mock data for Paymentus clone

export const navigationItems = [
  {
    title: "Who We Serve",
    items: [
      "Utilities",
      "Financial Services", 
      "Insurance",
      "Government",
      "Telecommunications",
      "Healthcare"
    ]
  },
  {
    title: "Solutions",
    items: [
      "Bill Presentment",
      "Payment Processing",
      "Customer Communications",
      "Analytics & Insights",
      "API Integration",
      "Mobile Solutions"
    ]
  },
  {
    title: "Company",
    items: [
      "About Us",
      "Leadership",
      "Careers",
      "News",
      "Investor Relations",
      "ESG Report"
    ]
  },
  {
    title: "Learn",
    items: [
      "Resources",
      "Case Studies",
      "Webinars",
      "Documentation",
      "Support",
      "Training"
    ]
  }
];

export const heroContent = {
  title: "Intelligent Simplified Payments.",
  subtitle: "Meet intelligence that pays.",
  description: "From actionable data and insights to billing and payment options for all, give your customers, staff, and entire enterprise the intelligence and simplicity to transform your business. Unleash your full potential and turn every transaction into a best-in-class interaction today.",
  ctaText: "LET'S GET STARTED"
};

export const servicesData = [
  {
    title: "More Secure Way to Pay Bills",
    description: "Paymentus' AI-powered, patented bill pay assistant and omnichannel wallet are fundamentally simplifying how bills are presented, understood, and paid. See how it delivers 4x faster payments.",
    ctaText: "START NOW",
    image: "/api/placeholder/600/400"
  },
  {
    title: "Intuitive Interactions, Bill Delivery & Payments for Billers",
    subtitle: "BILLING & PAYMENTS",
    description: "Transform how your customers experience billing and payments with our intelligent platform.",
    image: "/api/placeholder/800/500"
  }
];

export const statsData = [
  { number: "2,500+", label: "Billers Served" },
  { number: "597M+", label: "Annual Payments" },
  { number: "4x", label: "Faster Payments" },
  { number: "99.9%", label: "Uptime SLA" }
];

export const quickLinksData = [
  {
    title: "Bill Pay FAQs",
    description: "Let us help you find answers to get your bill paid quickly and simply.",
    ctaText: "GET ANSWERS"
  },
  {
    title: "Become a Partner",
    description: "Speak with our business team to explore our unique opportunities.",
    ctaText: "CONTACT US"
  },
  {
    title: "Join Our Team",
    description: "Build a career at the forefront of billing and payments interactions.",
    ctaText: "VIEW OPENINGS"
  }
];

export const footerLinks = {
  company: [
    { name: "Instant Payment Network", href: "#" },
    { name: "Who We Serve", href: "#" },
    { name: "Join Our Team", href: "#" },
    { name: "Virtual Learning", href: "#" },
    { name: "Investor Relations", href: "#" },
    { name: "ESG Report", href: "#" }
  ],
  legal: [
    { name: "Privacy Notice", href: "#" },
    { name: "Privacy Notice to California Residents", href: "#" },
    { name: "Cigna MRF", href: "#" },
    { name: "Cookie Notice", href: "#" },
    { name: "Website Conditions of Use", href: "#" },
    { name: "Do Not Sell or Share My Personal Info", href: "#" }
  ]
};

// Mock user data
export const mockUsers = [
  {
    id: "1",
    email: "john.doe@email.com",
    name: "John Doe",
    phone: "(555) 123-4567",
    address: "123 Main St, Charlotte, NC 28202"
  },
  {
    id: "2", 
    email: "jane.smith@email.com",
    name: "Jane Smith",
    phone: "(555) 987-6543",
    address: "456 Oak Ave, Raleigh, NC 27601"
  }
];

// Mock bills/payments data
export const mockBills = [
  {
    id: "bill_001",
    userId: "1",
    billerName: "Duke Energy",
    accountNumber: "****5678",
    amount: 127.45,
    dueDate: "2024-02-15",
    status: "pending",
    billType: "utility",
    description: "Electric Service - January 2024"
  },
  {
    id: "bill_002", 
    userId: "1",
    billerName: "Charlotte Water",
    accountNumber: "****9012",
    amount: 89.32,
    dueDate: "2024-02-20",
    status: "pending",
    billType: "utility",
    description: "Water & Sewer - January 2024"
  },
  {
    id: "bill_003",
    userId: "1", 
    billerName: "Spectrum Internet",
    accountNumber: "****3456",
    amount: 74.99,
    dueDate: "2024-02-12",
    status: "paid",
    billType: "telecommunications",
    description: "Internet Service - February 2024"
  },
  {
    id: "bill_004",
    userId: "2",
    billerName: "State Farm Insurance",
    accountNumber: "****7890",
    amount: 156.80,
    dueDate: "2024-02-25",
    status: "pending", 
    billType: "insurance",
    description: "Auto Insurance - February 2024"
  }
];

export const mockTransactions = [
  {
    id: "txn_001",
    userId: "1",
    billId: "bill_003",
    amount: 74.99,
    paymentMethod: "Credit Card ****1234",
    timestamp: "2024-01-15T10:30:00Z",
    status: "completed",
    confirmationNumber: "PAY123456789"
  },
  {
    id: "txn_002",
    userId: "1", 
    billId: "bill_001",
    amount: 127.45,
    paymentMethod: "Bank Account ****5678",
    timestamp: "2024-01-10T14:22:00Z",
    status: "completed",
    confirmationNumber: "PAY987654321"
  },
  {
    id: "txn_003",
    userId: "2",
    billId: "bill_004", 
    amount: 156.80,
    paymentMethod: "PayPal",
    timestamp: "2024-01-08T09:15:00Z", 
    status: "completed",
    confirmationNumber: "PAY456789123"
  }
];

export const paymentMethods = [
  {
    id: "pm_001",
    userId: "1",
    type: "credit_card",
    last4: "1234",
    brand: "Visa",
    expiryMonth: 12,
    expiryYear: 2026,
    isDefault: true
  },
  {
    id: "pm_002", 
    userId: "1",
    type: "bank_account",
    last4: "5678",
    bankName: "Bank of America",
    accountType: "checking",
    isDefault: false
  },
  {
    id: "pm_003",
    userId: "2",
    type: "paypal",
    email: "jane.smith@email.com",
    isDefault: true
  }
];

// Dashboard metrics
export const dashboardMetrics = {
  totalPayments: 847,
  monthlyVolume: 12459.67,
  successRate: 99.8,
  avgProcessingTime: 2.3
};