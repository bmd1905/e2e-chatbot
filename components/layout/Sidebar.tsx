import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import {
  Triangle,
  SquareTerminal,
  Bot,
  Code2,
  Book,
  Settings2,
  LifeBuoy,
  SquareUser,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function Sidebar() {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <aside className="inset-y fixed left-0 z-20 flex h-full flex-col border-r">
      <div className="border-b p-2">
        <Button variant="outline" size="icon" aria-label="Home">
          <Triangle className="size-5 fill-foreground" />
        </Button>
      </div>
      <nav className="grid gap-1 p-2">
        <SidebarItem icon={SquareTerminal} label="Playground" href="/dashboard" />
        <SidebarItem icon={Bot} label="Models" href="/models" />
        <SidebarItem icon={Code2} label="API" href="/api" />
        <SidebarItem icon={Book} label="Documentation" href="/docs" />
        <SidebarItem icon={Settings2} label="Settings" href="/settings" />
      </nav>
      <nav className="mt-auto grid gap-1 p-2">
        <SidebarItem icon={LifeBuoy} label="Help" href="/help" />
        <SidebarItem icon={SquareUser} label="Account" href="/account" />
        <SidebarItem icon={LogOut} label="Logout" onClick={handleLogout} />
      </nav>
    </aside>
  );
}

interface SidebarItemProps {
  icon: React.ElementType;
  label: string;
  href?: string;
  onClick?: () => void;
}

function SidebarItem({ icon: Icon, label, href, onClick }: SidebarItemProps) {
  const router = useRouter();
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (href) {
      router.push(href);
    }
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="rounded-lg"
          aria-label={label}
          onClick={handleClick}
        >
          <Icon className="size-5" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side="right" sideOffset={5}>
        {label}
      </TooltipContent>
    </Tooltip>
  );
}