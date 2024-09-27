import React from 'react';
import {
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import ModelSelector from '../ModelSelector';
import AgentTypeSelector from '../AgentTypeSelector';

export default function SettingsDrawer() {
  return (
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
            <Label htmlFor="model">Model</Label>
            <ModelSelector />
          </div>
          <div className="grid gap-3">
            <Label htmlFor="agent-type-mobile">Agent Type</Label>
            <AgentTypeSelector />
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
  );
}