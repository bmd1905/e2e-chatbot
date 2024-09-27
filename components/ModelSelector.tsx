import React from 'react';
import { Rabbit, Bird, Turtle } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function ModelSelector() {
  return (
    <Select>
      <SelectTrigger
        id="model"
        className="items-start [&_[data-description]]:hidden"
      >
        <SelectValue placeholder="Select a model" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="genesis">
          <div className="flex items-start gap-3 text-muted-foreground">
            <Rabbit className="size-5" />
            <div className="grid gap-0.5">
              <p>
                Neural{" "}
                <span className="font-medium text-foreground">
                  Genesis
                </span>
              </p>
              <p className="text-xs" data-description>
                Our fastest model for general use cases.
              </p>
            </div>
          </div>
        </SelectItem>
        <SelectItem value="explorer">
          <div className="flex items-start gap-3 text-muted-foreground">
            <Bird className="size-5" />
            <div className="grid gap-0.5">
              <p>
                Neural{" "}
                <span className="font-medium text-foreground">
                  Explorer
                </span>
              </p>
              <p className="text-xs" data-description>
                Performance and speed for efficiency.
              </p>
            </div>
          </div>
        </SelectItem>
        <SelectItem value="quantum">
          <div className="flex items-start gap-3 text-muted-foreground">
            <Turtle className="size-5" />
            <div className="grid gap-0.5">
              <p>
                Neural{" "}
                <span className="font-medium text-foreground">
                  Quantum
                </span>
              </p>
              <p className="text-xs" data-description>
                The most powerful model for complex computations.
              </p>
            </div>
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}