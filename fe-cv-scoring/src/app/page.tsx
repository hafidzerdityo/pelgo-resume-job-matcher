"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { CandidateProfile, MatchJob } from "@/types";
import { useMatches } from "@/hooks/useMatches";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogTitle, DialogTrigger, DialogHeader, DialogDescription } from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem
} from "@/components/ui/dropdown-menu";
import { Clock, Loader2, CheckCircle2, XCircle, Search, BrainCircuit, MoreVertical, RotateCcw } from "lucide-react";
import Link from "next/link";

function JobDetailContent({ match }: { match: MatchJob }) {
  const formattedDate = new Date(match.created_at).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true
  });

  if (match.status === "pending") {
    return (
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between pb-4 border-b">
          <h3 className="font-semibold text-slate-500 flex items-center tracking-tight"><Clock className="mr-2 h-4 w-4" /> Queued</h3>
          <span className="text-xs text-slate-400 font-medium">{formattedDate}</span>
        </div>
        <p className="text-sm bg-slate-50 p-4 rounded-md font-mono text-slate-600 border border-slate-100">{match.source_url || match.job_description}</p>
      </div>
    );
  }

  if (match.status === "processing") {
    return (
      <div className="space-y-4 pt-4 animate-pulse">
        <div className="flex items-center justify-between pb-4 border-b">
          <h3 className="font-semibold text-blue-600 flex items-center tracking-tight"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Scoring with Algorithm...</h3>
          <span className="text-xs text-slate-400 font-medium">{formattedDate}</span>
        </div>
        <p className="text-sm bg-blue-50/50 p-4 rounded-md font-mono text-blue-800 border border-blue-100">{match.source_url || match.job_description}</p>
      </div>
    );
  }

  if (match.status === "failed" || match.status === "dead") {
    return (
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between pb-4 border-b">
          <h3 className={`font-semibold ${match.status === "dead" ? "text-slate-700" : "text-red-600"} flex items-center tracking-tight`}>
            {match.status === "dead" ? <XCircle className="mr-2 h-4 w-4" /> : <XCircle className="mr-2 h-4 w-4" />}
            {match.status === "dead" ? "Dead (Max Retries Reached)" : "Failed"}
          </h3>
          <span className="text-xs text-slate-400 font-medium">{formattedDate}</span>
        </div>
        <div className="space-y-2">
          <p className={`text-sm ${match.status === "dead" ? "bg-slate-100 text-slate-600" : "bg-red-50 text-red-600"} p-4 rounded-md border border-slate-200`}>
            {match.error_message}
          </p>
          <p className="text-[10px] text-slate-400 font-mono">Retries: {match.retry_count}/3</p>
        </div>
      </div>
    );
  }

  // Completed
  return (
    <div className="max-h-[70vh] overflow-y-auto pr-4 custom-scrollbar -mr-4">
      <div className="space-y-6 pt-4">
        <div className="flex items-center justify-between pb-4 border-b">
          <h3 className="font-bold text-emerald-600 flex items-center text-lg tracking-tight">
            <CheckCircle2 className="mr-2 h-5 w-5" /> Overall Score: {match.overall_score}%
          </h3>
          <span className="text-xs text-slate-400 font-medium">{formattedDate}</span>
        </div>

        <div className="text-sm text-slate-600 p-3 bg-slate-50/50 rounded-md border border-slate-100">
          <span className="font-semibold block mb-1 text-slate-700">Target Description / URL:</span>
          <div className="font-mono text-xs break-all">{match.source_url || match.job_description}</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs text-slate-800">
              <span>Skill Match</span>
              <span className="font-bold text-slate-900">{match.skill_score}%</span>
            </div>
            <Progress value={match.skill_score || 0} className="h-1.5" />
          </div>
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs text-slate-800">
              <span>Experience Match</span>
              <span className="font-bold text-slate-900">{match.experience_score}%</span>
            </div>
            <Progress value={match.experience_score || 0} className="h-1.5" />
          </div>
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs text-slate-800">
              <span>Location Match</span>
              <span className="font-bold text-slate-900">{match.location_score}%</span>
            </div>
            <Progress value={match.location_score || 0} className="h-1.5" />
          </div>
        </div>

        <div className="space-y-5">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Matched Skills</span>
            <div className="flex flex-wrap gap-1.5">
              {match.matched_skills && match.matched_skills.length > 0 ? (
                match.matched_skills.map((s) => <Badge key={s} variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">{s}</Badge>)
              ) : (
                <span className="text-xs text-slate-400 italic">None</span>
              )}
            </div>
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Missing Skills</span>
            <div className="flex flex-wrap gap-1.5">
              {match.missing_skills && match.missing_skills.length > 0 ? (
                match.missing_skills.map((s) => <Badge key={s} variant="outline" className="bg-rose-50 text-rose-700 border-rose-200">{s}</Badge>)
              ) : (
                <span className="text-xs text-slate-400 italic">None</span>
              )}
            </div>
          </div>
        </div>

        <div className="bg-slate-800 text-slate-50 p-4 rounded-xl shadow-inner mt-2">
          <div className="text-[10px] text-slate-400 uppercase font-bold tracking-widest mb-1.5">AI Recommendation</div>
          <p className="text-sm leading-relaxed">{match.recommendation}</p>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [candidates, setCandidates] = useState<CandidateProfile[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<string>("");
  const [jobInputs, setJobInputs] = useState<string[]>([""]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  // For managing the View dialog manually to avoid nesting issues with Dropdown
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<MatchJob | null>(null);

  const { matches, pagination, loading, refetch } = useMatches(selectedCandidate || null, currentPage, 6);

  // Reset page when switching candidate
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedCandidate]);

  useEffect(() => {
    async function loadCandidates() {
      try {
        const res = await api.get("/candidates");
        setCandidates(res.data);
      } catch {
        toast.error("Failed to load candidates");
      }
    }
    loadCandidates();
  }, []);

  const addJobField = () => {
    if (jobInputs.length < 10) {
      setJobInputs([...jobInputs, ""]);
    } else {
      toast.error("Maximum 10 jobs per batch allowed.");
    }
  };

  const removeJobField = (index: number) => {
    if (jobInputs.length > 1) {
      const newInputs = [...jobInputs];
      newInputs.splice(index, 1);
      setJobInputs(newInputs);
    }
  };

  const handleInputChange = (index: number, value: string) => {
    const newInputs = [...jobInputs];
    newInputs[index] = value;
    setJobInputs(newInputs);
  };

  const handleSubmit = async () => {
    if (!selectedCandidate) return toast.error("Please select a candidate first.");

    // Filter out empty inputs and determine if it's a URL
    const jobs = jobInputs
      .map((j) => {
        const txt = j.trim();
        if (txt.startsWith("http://") || txt.startsWith("https://")) {
          return { url: txt };
        }
        return { text: txt };
      })
      .filter((j) => (j.text && j.text.length > 0) || (j.url && j.url.length > 0));

    if (jobs.length === 0) return toast.error("Please enter at least one job description.");

    setIsSubmitting(true);
    toast.info(`Submitting ${jobs.length} jobs for analysis...`);

    try {
      await api.post("/matches", {
        candidate_id: selectedCandidate,
        jobs,
      });
      toast.success("Succesfully placed on the Background Queue");
      setJobInputs([""]);
      setCurrentPage(1);
      refetch();
    } catch {
      toast.error("Failed to submit jobs");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = async (jobId: string) => {
    try {
      await api.post(`/matches/${jobId}/retry`);
      toast.success("Job re-queued successfully");
      refetch();
    } catch (err: any) {
      const msg = err.response?.data?.detail?.message || "Failed to retry job";
      toast.error(msg);
    }
  };
  return (
    <div className="flex flex-col gap-10">
      <header className="border-b pb-4">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
          Resume Job Matcher
        </h1>
        <p className="text-slate-500 mt-2 font-medium">
          Select a candidate profile and paste job descriptions (or URLs) to evaluate async fit scores.
        </p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        <div className="xl:col-span-4 space-y-6 top-8 sticky">
          <Card className="shadow-lg border-slate-200">
            <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
              <CardTitle>1. Select Candidate</CardTitle>
              <CardDescription>Pick an existing candidate from DB.</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <Select value={selectedCandidate} onValueChange={(val) => setSelectedCandidate(val || "")}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a candidate..." />
                </SelectTrigger>
                <SelectContent>
                  {candidates.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Display active candidate details */}
              {(() => {
                const active = candidates.find(c => c.id === selectedCandidate);
                if (!active) return null;

                return (
                  <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200/60 shadow-sm animate-in fade-in zoom-in-95 duration-200">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-slate-800 tracking-tight">{active.name}</h4>
                      <Badge variant="secondary" className="bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200/50">
                        {active.seniority}
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-500 space-y-2">
                      <div className="grid grid-cols-2 gap-2">
                        <p><span className="font-medium text-slate-600">Location:</span> {active.location || "Remote"}</p>
                        <p><span className="font-medium text-slate-600">Exp:</span> {active.experience_years} years</p>
                      </div>
                      <div className="pt-2 border-t border-slate-200/50">
                        <span className="font-medium text-slate-600 block mb-1.5">Registered Skills:</span>
                        <div className="flex flex-wrap gap-1">
                          {active.skills.map(s => (
                            <span key={s} className="px-1.5 py-0.5 bg-slate-200/60 text-slate-600 rounded text-[10px] font-medium tracking-wide">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-200/50">
                        <span className="font-medium text-slate-600 block mb-1.5 text-xs">Resume Preview:</span>
                        {active.resume_text ? (
                          <div className="bg-slate-900/5 p-2 rounded border border-slate-200/40 max-h-[120px] overflow-y-auto text-[10px] font-mono leading-relaxed text-slate-600 custom-scrollbar whitespace-pre-wrap">
                            {active.resume_text}
                          </div>
                        ) : (
                          <div className="pt-1">
                            <span className="text-xs text-slate-400 italic font-medium">No resume text provided in DB.</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })()}
            </CardContent>
          </Card>

          <Card className="shadow-lg border-slate-200">
            <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
              <CardTitle>2. Target Jobs</CardTitle>
              <CardDescription>Paste job descriptions or URLs (up to 10).</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {jobInputs.map((input, index) => (
                  <div key={index} className="space-y-2 relative group">
                    <div className="flex items-center justify-between">
                      <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Job #{index + 1}</label>
                      {jobInputs.length > 1 && (
                        <button
                          onClick={() => removeJobField(index)}
                          className="text-[10px] font-bold text-rose-500 hover:text-rose-700 uppercase tracking-widest transition-colors"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    <Textarea
                      placeholder="Paste job description or URL here..."
                      className="min-h-[120px] resize-none font-mono text-xs tracking-tight border-slate-200 focus:border-blue-400 transition-all"
                      value={input}
                      onChange={(e) => handleInputChange(index, e.target.value)}
                    />
                  </div>
                ))}
              </div>

              <Button
                variant="outline"
                className="w-full border-dashed border-2 border-slate-200 text-slate-500 hover:text-blue-600 hover:border-blue-200 transition-all text-xs font-bold uppercase tracking-wider"
                onClick={addJobField}
                disabled={jobInputs.length >= 10 || isSubmitting}
              >
                + Add Another Job
              </Button>

              <div className="pt-4 border-t">
                <Button
                  className="w-full font-semibold shadow-md bg-blue-600 hover:bg-blue-700 text-white transition-all"
                  onClick={handleSubmit}
                  disabled={isSubmitting || jobInputs.every(i => !i.trim()) || !selectedCandidate}
                >
                  {isSubmitting ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing Batch...</>
                  ) : `Run Match Analysis (${jobInputs.filter(i => i.trim()).length} Jobs)`}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="xl:col-span-8 space-y-6">
          <div className="bg-blue-50/40 p-5 rounded-xl border border-blue-100/60 shadow-sm mb-2">
            <h4 className="text-[11px] font-bold text-blue-700 uppercase tracking-widest mb-3 flex items-center">
              <BrainCircuit className="h-3.5 w-3.5 mr-2" />
              Scoring Methodology
            </h4>
            <p className="text-xs text-slate-600 mb-4">
              Using <strong>LLM</strong> to analyze deep semantic fit between candidate experience and job requirements.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Skills (65%)</span>
                <p className="text-[10px] text-slate-500 leading-tight">Semantic overlap between profile and description.</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Experience (30%)</span>
                <p className="text-[10px] text-slate-500 leading-tight">AI evaluation of career progression and seniority.</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Location (5%)</span>
                <p className="text-[10px] text-slate-500 leading-tight">AI evaluation of location suitability.</p>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-blue-100/50 text-[9px] text-blue-600 font-bold italic uppercase tracking-wider">
              Note: Results are generated asynchronously by background workers.
            </div>
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold tracking-tight">Match Results</h2>
            {loading && <div className="text-xs flex items-center text-slate-500 font-medium"><Loader2 className="h-3 w-3 mr-1.5 animate-spin" /> Syncing...</div>}
          </div>

          {!selectedCandidate ? (
            <div className="border border-dashed border-slate-300 rounded-xl p-12 text-center flex flex-col items-center justify-center text-slate-500 bg-white shadow-sm">
              <div className="rounded-full bg-slate-100 p-3 mb-4">
                <Clock className="h-6 w-6 text-slate-400" />
              </div>
              <h3 className="text-sm font-semibold text-slate-900 mb-1">Awaiting Candidate</h3>
              <p className="text-xs max-w-[250px]">Select a candidate profile from the dropdown panel to view scoring history.</p>
            </div>
          ) : matches.length === 0 ? (
            <div className="border border-dashed border-slate-300 rounded-xl p-12 text-center bg-white shadow-sm">
              <h3 className="text-sm font-semibold text-slate-900 mb-1">No Matches Found</h3>
              <p className="text-xs text-slate-500">Submit a job description on the left to begin.</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between h-auto">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader className="bg-slate-50/80">
                    <TableRow>
                      <TableHead className="w-[120px]">Date</TableHead>
                      <TableHead className="w-[120px]">Status</TableHead>
                      <TableHead className="max-w-[300px]">Description</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                      <TableHead className="w-[100px] text-center">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {matches.map((m) => (
                      <TableRow key={m.id} className="hover:bg-slate-50/50">
                        <TableCell className="text-xs text-slate-500 whitespace-nowrap align-middle">
                          {new Date(m.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </TableCell>
                        <TableCell className="align-middle">
                          {m.status === "pending" && <Badge variant="outline" className="bg-slate-100 text-slate-600"><Clock className="h-3 w-3 mr-1" /> Queued</Badge>}
                          {m.status === "processing" && <Badge variant="secondary" className="bg-blue-50 text-blue-600 animate-pulse border border-blue-200"><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Scoring</Badge>}
                          {m.status === "failed" && <Badge variant="destructive" className="bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"><XCircle className="h-3 w-3 mr-1" /> Failed</Badge>}
                          {m.status === "dead" && <Badge variant="outline" className="bg-slate-800 text-white border-slate-900"><XCircle className="h-3 w-3 mr-1" /> Dead</Badge>}
                          {m.status === "completed" && <Badge variant="default" className="bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100"><CheckCircle2 className="h-3 w-3 mr-1" /> Done</Badge>}
                        </TableCell>
                        <TableCell className="align-middle text-xs font-mono text-slate-500 truncate max-w-[200px] sm:max-w-[300px]">
                          {m.source_url || m.job_description}
                        </TableCell>
                        <TableCell className="text-right align-middle font-medium">
                          {m.overall_score ? `${m.overall_score}%` : "-"}
                        </TableCell>
                        <TableCell className="text-center align-middle">
                          <DropdownMenu>
                            <DropdownMenuTrigger className="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-500">
                              <MoreVertical className="h-4 w-4" />
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                              <DropdownMenuItem
                                onClick={() => {
                                  setSelectedJob(m);
                                  setViewDialogOpen(true);
                                }}
                              >
                                <Search /> View
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                disabled={m.status !== "failed"}
                                onClick={() => handleRetry(m.id)}
                                className="text-orange-600 focus:text-orange-700"
                              >
                                <RotateCcw /> Retry
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
                <DialogContent className="max-w-xl">
                  <DialogHeader>
                    <DialogTitle>Match Evaluation Details</DialogTitle>
                    <DialogDescription>Review complete metrics and semantic overlaps calculated by AI.</DialogDescription>
                  </DialogHeader>
                  {selectedJob && <JobDetailContent match={selectedJob} />}
                </DialogContent>
              </Dialog>

              {pagination && Math.ceil(pagination.total / pagination.limit) > 1 && (
                <div className="flex items-center justify-between p-4 border-t border-slate-100 bg-slate-50/30">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="shadow-sm"
                  >
                    Previous
                  </Button>
                  <span className="text-xs text-slate-500 font-medium tracking-wide">
                    Page {currentPage} of {Math.ceil(pagination.total / pagination.limit)}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.min(Math.ceil(pagination.total / pagination.limit), p + 1))}
                    disabled={currentPage === Math.ceil(pagination.total / pagination.limit)}
                    className="shadow-sm"
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
