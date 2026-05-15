import { AlertTriangle, CheckCircle2 } from "lucide-react";

import { getProjectTelemetry } from "@/app/actions/get-project-telemetry";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export async function UsageCard() {
  const telemetry = await getProjectTelemetry();

  if (!telemetry.ok) {
    return (
      <Card className="border-amber-200 bg-amber-50/70">
        <CardHeader>
          <div className="flex items-center gap-2 text-amber-700">
            <AlertTriangle className="size-5" />
            <Badge variant="secondary">{telemetry.status}</Badge>
          </div>
          <CardTitle>Usage telemetry unavailable</CardTitle>
          <CardDescription>{telemetry.message}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const { data } = telemetry;
  const remaining = Math.max(data.monthly_quota - data.usage_count, 0);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <div>
            <CardTitle>Project usage</CardTitle>
            <CardDescription>Project {data.project_id}</CardDescription>
          </div>
          <Badge className="gap-1 bg-emerald-600 text-white">
            <CheckCircle2 className="size-3.5" /> Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-3xl font-semibold tracking-tight">
                {data.usage_count}
                <span className="text-base font-normal text-muted-foreground">
                  /{data.monthly_quota}
                </span>
              </p>
              <p className="text-sm text-muted-foreground">
                {remaining} requests remaining this cycle
              </p>
            </div>
            <p className="text-sm font-medium">{data.percentage}% used</p>
          </div>
          <Progress value={Math.min(data.percentage, 100)} />
        </div>

        <div className="rounded-lg border bg-muted/40 p-4 text-sm">
          <p className="text-muted-foreground">Next reset</p>
          <p className="font-medium">{data.reset_date}</p>
        </div>
      </CardContent>
    </Card>
  );
}
