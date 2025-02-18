# Social Media Automation Tool

A comprehensive web-based social media automation tool that allows users to automate actions (follow/unfollow) across multiple platforms: Instagram, X (Twitter), LinkedIn, Facebook, YouTube, Pinterest, and Substack.

## Features

- Multi-platform support: Instagram, X (Twitter), LinkedIn, Facebook, YouTube, Pinterest, and Substack
- User-friendly interface for platform selection and action configuration
- Automated follow/unfollow actions
- URL management system with import/export capabilities
- Scheduling feature for automated tasks
- Real-time task monitoring and progress tracking
- Detailed activity logs with filtering options
- Secure credential management for each platform

## Technologies Used

- Next.js 13+ with App Router
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- Zustand for state management
- Shadcn UI components
- Lucide React icons

## Setup Instructions

1. Clone the repository:
   \`\`\`
   git clone https://github.com/your-username/social-media-automation-tool.git
   cd social-media-automation-tool
   \`\`\`

2. Install dependencies:
   \`\`\`
   npm install
   \`\`\`

3. Create a \`.env.local\` file in the root directory and add any necessary environment variables.

4. Run the development server:
   \`\`\`
   npm run dev
   \`\`\`

5. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Usage

1. Select a social media platform from the main page.
2. Configure the action (follow/unfollow) and target (followers/following).
3. Enter the profile URL and set the quantity of actions to perform.
4. Click "LET'S GO!" to start the automation process.
5. Monitor progress in the Logs tab and manage schedules in the Schedule tab.

## Project Structure

\`\`\`
social-media-automation-tool/
├── app/
│   ├── automation/
│   │   └── [platform]/
│   │       └── page.tsx
│   └── page.tsx
├── components/
│   ├── action-selector.tsx
│   ├── logs-manager.tsx
│   ├── platform-icons.tsx
│   ├── platform-selector.tsx
│   ├── schedule-manager.tsx
│   ├── site-header.tsx
│   ├── status-bar.tsx
│   ├── status-bar.module.css
│   └── url-manager.tsx
├── lib/
│   └── store.ts
├── public/
├── styles/
│   └── globals.css
├── .env.local
├── next.config.js
├── package.json
├── README.md
└── tsconfig.json
\`\`\`

## Contributing

We welcome contributions to improve the Social Media Automation Tool. Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (\`git checkout -b feature/AmazingFeature\`)
3. Make your changes
4. Commit your changes (\`git commit -m 'Add some AmazingFeature'\`)
5. Push to the branch (\`git push origin feature/AmazingFeature\`)
6. Open a Pull Request

## License

This project is licensed under the MIT License. See the \`LICENSE\` file for details.

## Disclaimer

This tool is for educational purposes only. Users are responsible for complying with the terms of service of each social media platform and any applicable laws and regulations.
\`\`\`

# Trigger deployment
# Trigger deployment
# Trigger deployment
# Trigger deployment

## Test Update
This is a test update to verify our GitHub connection is working properly - Updated on: 2024-01-31

## Authentication Test
Testing GitHub authentication - Updated: 2024-01-31
