import React from 'react';
import { Layers, Sparkles, MessageSquare } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function AgentTypeSelector() {
  return (
    <Select>
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
  );
}