import {
  Bird,
  Book,
  Bot,
  Code2,
  CornerDownLeft,
  LifeBuoy,
  Mic,
  Rabbit,
  Settings,
  Settings2,
  Share,
  SquareTerminal,
  SquareUser,
  Triangle,
  Turtle,
  LogOut,
  Layers,
  Sparkles,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Sun,
  Moon,
  Send,
  Clipboard,
  Check,
  User,
  Zap,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from "@/components/ui/tooltip";
import { useState, useEffect, useRef, KeyboardEvent } from 'react'
import api from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useTheme } from "next-themes"
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { motion } from "framer-motion";
import './animations.css'; // Import the CSS file for animations

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Dashboard() {
  const { logout } = useAuth()
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [agentType, setAgentType] = useState('simple')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { setTheme, theme } = useTheme()
  const [pendingMessage, setPendingMessage] = useState<Message | null>(null);
  const [copiedResponse, setCopiedResponse] = useState(false);
  const [copiedCode, setCopiedCode] = useState<{[key: number]: boolean}>({});
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingDots, setThinkingDots] = useState('');
  const [selectedModel, setSelectedModel] = useState('gpt-4o')

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isThinking) {
      interval = setInterval(() => {
        setThinkingDots(dots => dots.length < 3 ? dots + '.' : '');
      }, 500);
    }
    return () => clearInterval(interval);
  }, [isThinking]);

  const handleSendMessage = async (e: React.FormEvent | KeyboardEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    setIsLoading(true);
    setIsThinking(true);
    const userMessage: Message = { role: 'user', content: inputMessage };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setPendingMessage({ role: 'assistant', content: '' });
    setInputMessage('');

    try {
      const response = await api.post('/api/v1/chatbot/chat', {
        prompt: userMessage.content,
        agent_type: agentType,
        model: selectedModel,
        history: messages,
      });
      const aiMessage: Message = { role: 'assistant', content: response.data.response };
      setMessages(prevMessages => [...prevMessages, aiMessage]);
      setPendingMessage(null);
    } catch (error) {
      console.error('Error sending message:', error);
      setPendingMessage(null);
    } finally {
      setIsLoading(false);
      setIsThinking(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const handleFeedback = async (messageIndex: number, isPositive: boolean) => {
    try {
      await api.post('/api/v1/chatbot/feedback', {
        message_id: messageIndex,
        is_positive: isPositive
      })
      // Optionally update UI to show feedback has been recorded
    } catch (error) {
      console.error('Error sending feedback:', error)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  const copyToClipboard = (text: string, type: 'response' | 'code', index?: number) => {
    navigator.clipboard.writeText(text).then(() => {
      if (type === 'response') {
        setCopiedResponse(true);
        setTimeout(() => setCopiedResponse(false), 2000);
      } else if (type === 'code' && index !== undefined) {
        setCopiedCode(prev => ({ ...prev, [index]: true }));
        setTimeout(() => setCopiedCode(prev => ({ ...prev, [index]: false })), 2000);
      }
    });
  };

  return (
    <TooltipProvider>
      <div className="grid h-screen w-full pl-[56px]">
        <aside className="inset-y fixed left-0 z-20 flex h-full flex-col border-r">
          <div className="border-b p-2">
            <Button variant="outline" size="icon" aria-label="Home">
              <Triangle className="size-5 fill-foreground" />
            </Button>
          </div>
          <nav className="mt-auto grid gap-1 p-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="mt-auto rounded-lg"
                  aria-label="Logout"
                  onClick={handleLogout}
                >
                  <LogOut className="size-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" sideOffset={5}>
                Logout
              </TooltipContent>
            </Tooltip>
          </nav>
        </aside>
        <div className="flex flex-col">
          <header className="sticky top-0 z-10 flex h-[57px] items-center gap-1 border-b bg-background px-4">
            <h1 className="text-xl font-semibold">Playground</h1>
            <Drawer>
              <DrawerTrigger asChild>
                <Button variant="ghost" size="icon" className="md:hidden">
                  <Settings className="size-4" />
                  <span className="sr-only">Settings</span>
                </Button>
              </DrawerTrigger>
              <DrawerContent className="max-h-[80vh]">
                <DrawerHeader>
                  <DrawerTitle>Configuration</DrawerTitle>
                  <DrawerDescription>
                    Configure the settings for the model and agent type.
                  </DrawerDescription>
                </DrawerHeader>
                <form className="grid w-full items-start gap-6 overflow-auto p-4 pt-0">
                  <fieldset className="grid gap-6 rounded-lg border p-4">
                    <legend className="-ml-1 px-1 text-sm font-medium">
                      Settings
                    </legend>
                    <div className="grid gap-3">
                      <Label htmlFor="agent-type-mobile">Agent Type</Label>
                      <Select value={agentType} onValueChange={setAgentType}>
                        <SelectTrigger
                          id="agent-type-mobile"
                          className="items-start [&_[data-description]]:hidden"
                        >
                          <SelectValue placeholder="Select an agent type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="multi_step">
                            <div className="flex items-start gap-3 text-muted-foreground">
                              <Layers className="size-5" />
                              <div className="grid gap-0.5">
                                <p>
                                  <span className="font-medium text-foreground">
                                    Multi-Step Agent
                                  </span>
                                </p>
                                <p className="text-xs" data-description>
                                  Breaks down complex tasks into subtasks.
                                </p>
                              </div>
                            </div>
                          </SelectItem>
                          <SelectItem value="prompt_optim">
                            <div className="flex items-start gap-3 text-muted-foreground">
                              <Sparkles className="size-5" />
                              <div className="grid gap-0.5">
                                <p>
                                  <span className="font-medium text-foreground">
                                    Prompt Optimization
                                  </span>
                                </p>
                                <p className="text-xs" data-description>
                                  Refines prompts for better results.
                                </p>
                              </div>
                            </div>
                          </SelectItem>
                          <SelectItem value="simple">
                            <div className="flex items-start gap-3 text-muted-foreground">
                              <MessageSquare className="size-5" />
                              <div className="grid gap-0.5">
                                <p>
                                  <span className="font-medium text-foreground">
                                    Simple Chatbot
                                  </span>
                                </p>
                                <p className="text-xs" data-description>
                                  Basic conversational agent.
                                </p>
                              </div>
                            </div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-3">
                      <Label htmlFor="top-p">Top P</Label>
                      <Input id="top-p" type="number" placeholder="0.7" />
                    </div>
                    <div className="grid gap-3">
                      <Label htmlFor="top-k">Top K</Label>
                      <Input id="top-k" type="number" placeholder="0.0" />
                    </div>
                  </fieldset>
                  <fieldset className="grid gap-6 rounded-lg border p-4">
                    <legend className="-ml-1 px-1 text-sm font-medium">
                      Messages
                    </legend>
                    <div className="grid gap-3">
                      <Label htmlFor="role">Role</Label>
                      <Select defaultValue="system">
                        <SelectTrigger>
                          <SelectValue placeholder="Select a role" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="system">System</SelectItem>
                          <SelectItem value="user">User</SelectItem>
                          <SelectItem value="assistant">Assistant</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-3">
                      <Label htmlFor="content">Content</Label>
                      <Textarea id="content" placeholder="You are a..." />
                    </div>
                  </fieldset>
                </form>
              </DrawerContent>
            </Drawer>
            <Button
              variant="outline"
              size="sm"
              className="ml-auto gap-1.5 text-sm"
            >
              <Share className="size-3.5" />
              Share
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="ml-2"
            >
              <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </header>
          <main className="grid flex-1 gap-4 p-4 md:grid-cols-3 lg:grid-cols-4">
            <div className="relative flex h-full min-h-[50vh] flex-col rounded-xl bg-muted/50 p-4 lg:col-span-3">
              <ScrollArea className="flex-1 pr-4">
                {messages.map((msg, index) => (
                  <motion.div
                    key={index}
                    className={msg.role === 'assistant' ? 'response' : ''}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <Card className={`mb-4 ${msg.role === 'user' ? 'ml-auto' : 'mr-auto'} max-w-[80%]`}>
                      <CardContent className={`p-3 ${msg.role === 'user' ? '' : 'bg-secondary text-secondary-foreground'}`}>
                        <div className="flex items-start">
                          <div className="mr-3 mt-0.5">
                            {msg.role === 'user' ? (
                              <User className="h-6 w-6 text-primary" />
                            ) : (
                              <Bot className="h-6 w-6 text-primary" />
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="markdown-content">
                              <ReactMarkdown
                                components={{
                                  h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-4" {...props} />,
                                  h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mb-3" {...props} />,
                                  h3: ({ node, ...props }) => <h3 className="text-lg font-medium mb-2" {...props} />,
                                  p: ({ node, ...props }) => <p className="mb-4" {...props} />,
                                  ul: ({ node, ...props }) => <ul className="list-disc pl-6 mb-4" {...props} />,
                                  ol: ({ node, ...props }) => <ol className="list-decimal pl-6 mb-4" {...props} />,
                                  li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                                  blockquote: ({ node, ...props }) => (
                                    <blockquote className="border-l-4 border-primary pl-4 italic my-4" {...props} />
                                  ),
                                  code({ node, inline, className, children, ...props }) {
                                    const match = /language-(\w+)/.exec(className || '')
                                    return !inline && match ? (
                                      <div className="relative">
                                        <div className="absolute top-0 right-0 bg-muted text-muted-foreground text-xs px-2 py-1 rounded-bl">
                                          {match[1]}
                                          <button
                                            onClick={() => copyToClipboard(String(children), 'code', index)}
                                            className="ml-2 focus:outline-none"
                                          >
                                            {copiedCode[index] ? <Check size={14} /> : <Clipboard size={14} />}
                                          </button>
                                        </div>
                                        <SyntaxHighlighter
                                          style={tomorrow}
                                          language={match[1]}
                                          PreTag="div"
                                          className="rounded-md !mt-6 !mb-4"
                                          {...props}
                                        >
                                          {String(children).replace(/\n$/, '')}
                                        </SyntaxHighlighter>
                                      </div>
                                    ) : (
                                      <code className="bg-muted text-muted-foreground px-1 py-0.5 rounded" {...props}>
                                        {children}
                                      </code>
                                    )
                                  }
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                            {msg.role === 'assistant' && (
                              <Button
                                onClick={() => copyToClipboard(msg.content, 'response')}
                                className="mt-2 text-xs"
                                variant="outline"
                              >
                                {copiedResponse ? 'Copied!' : 'Copy Response'}
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
                {isThinking && (
                  <Card className="mb-4 mr-auto max-w-[80%]">
                    <CardContent className="p-3 bg-secondary text-secondary-foreground">
                      <div className="flex items-center space-x-2">
                        <span>Thinking</span>
                        <span className="w-8">{thinkingDots}</span>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </ScrollArea>
              <div className="mt-4">
                <Textarea
                  placeholder="Type your message here..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="min-h-[0px] resize-none p-2"
                  rows={2}
                />
                <div className="mt-2 flex justify-between items-center">
                  <Button variant="outline" size="icon">
                    <Mic className="h-4 w-4" />
                  </Button>
                  <Button 
                    onClick={handleSendMessage} 
                    disabled={isLoading || !inputMessage.trim()}
                    className="ml-auto"
                  >
                    {isLoading ? 'Sending...' : 'Send'}
                    <Send className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <div
              className="relative hidden flex-col items-start gap-8 md:flex"
              x-chunk="A settings form a configuring an AI model and messages."
            >
              <form className="grid w-full items-start gap-6">
                <fieldset className="grid gap-6 rounded-lg border p-4">
                  <legend className="-ml-1 px-1 text-sm font-medium">
                    Settings
                  </legend>
                  <div className="grid gap-3">
                    <Label htmlFor="model">Model</Label>
                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                      <SelectTrigger
                        id="model"
                        className="items-start [&_[data-description]]:hidden"
                      >
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="llama-3.1-70b-versatile">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Rabbit className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  LLama-3.1-70B
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Large language model for versatile tasks.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="gpt-4o">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Bird className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  GPT-4o
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Advanced model for complex reasoning.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="gpt-4o-mini">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Turtle className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  GPT-4o-mini
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Efficient model balancing performance and speed.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="gemini-1.5-flash">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Zap className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  Gemini Flash
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Fast and efficient for quick responses.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="gemini-1.5-pro">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Sparkles className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  Gemini Pro
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Advanced model for diverse applications.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="agent-type">Agent Type</Label>
                    <Select value={agentType} onValueChange={setAgentType}>
                      <SelectTrigger
                        id="agent-type"
                        className="items-start [&_[data-description]]:hidden"
                      >
                        <SelectValue placeholder="Select an agent type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="multi_step">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Layers className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  Multi-Step Agent
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Breaks down complex tasks into subtasks.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="prompt_optim">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Sparkles className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  Prompt Optimization
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Refines prompts for better results.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="simple">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <MessageSquare className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  Simple Chatbot
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Basic conversational agent.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </fieldset>
              </form>
            </div>
          </main>
        </div>
      </div>
    </TooltipProvider>
  );
}