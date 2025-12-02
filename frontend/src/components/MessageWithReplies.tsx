import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Mail, Send, Edit, X, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { useMessageAnalysis, useMessageReplies, Message } from '../hooks/useMessages';
import { messagesApi } from '../services/messages';
import { repliesApi } from '../services/replies';

interface MessageWithRepliesProps {
  message: Message;
  onReplyUsed?: () => void;
}

export const MessageWithReplies = ({ message, onReplyUsed }: MessageWithRepliesProps) => {
  const { analysis } = useMessageAnalysis(message.id);
  const { replies, refetch: refetchReplies } = useMessageReplies(message.id);
  const [expanded, setExpanded] = useState(false);
  const [selectedReply, setSelectedReply] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleUseSuggestion = async (suggestionId: string, content: string) => {
    try {
      await messagesApi.useSuggestion(suggestionId);
      setSelectedReply(suggestionId);
      setEditedContent(content);
      setIsEditing(false);
      refetchReplies();
      onReplyUsed?.();
    } catch (error) {
      console.error('Failed to use suggestion:', error);
    }
  };

  const handleEdit = (content: string) => {
    setEditedContent(content);
    setIsEditing(true);
  };

  const handleSend = async () => {
    if (!selectedReply) return;
    
    try {
      setIsSending(true);
      // First update the draft if edited
      if (isEditing && editedContent) {
        await repliesApi.editReply(selectedReply, editedContent);
      }
      // Then approve and send
      await repliesApi.approveReply(selectedReply);
      setSelectedReply(null);
      setEditedContent('');
      setIsEditing(false);
      refetchReplies();
      onReplyUsed?.();
    } catch (error) {
      console.error('Failed to send reply:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleReject = async (suggestionId: string) => {
    try {
      await messagesApi.deleteSuggestion(suggestionId);
      if (selectedReply === suggestionId) {
        setSelectedReply(null);
        setEditedContent('');
        setIsEditing(false);
      }
      refetchReplies();
    } catch (error) {
      console.error('Failed to reject suggestion:', error);
    }
  };

  const getPriorityColor = (score: number) => {
    if (score >= 0.7) return 'bg-red-100 dark:bg-red-900/30 border-red-600 dark:border-red-400 text-red-700 dark:text-red-300';
    if (score >= 0.4) return 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-600 dark:border-yellow-400 text-yellow-800 dark:text-yellow-300';
    return 'bg-green-100 dark:bg-green-900/30 border-green-600 dark:border-green-400 text-green-700 dark:text-green-300';
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 0.7) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  return (
    <Card className="border-2 border-border shadow-retro">
      <CardHeader className="cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Mail size={16} />
              <span className="text-xs font-bold text-muted-foreground uppercase">
                {message.platform}
              </span>
              {analysis && (
                <span className={`text-xs px-2 py-0.5 border-2 ${getPriorityColor(analysis.priority_score)}`}>
                  {getPriorityLabel(analysis.priority_score)}
                </span>
              )}
            </div>
            <CardTitle className="text-lg">{message.subject || 'No Subject'}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">From: {message.sender}</p>
            {analysis && (
              <p className="text-sm mt-2 text-muted-foreground italic">{analysis.summary}</p>
            )}
          </div>
          <Button variant="ghost" size="sm">
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </Button>
        </div>
      </CardHeader>

      {expanded && (
        <CardContent className="border-t-2 border-border pt-4">
          <div className="space-y-4">
            {/* Message Content */}
            <div className="p-3 bg-muted/50 border-2 border-border">
              <p className="text-sm whitespace-pre-wrap text-foreground">{message.content.substring(0, 500)}{message.content.length > 500 ? '...' : ''}</p>
            </div>

            {/* Smart Reply Suggestions */}
            {replies && replies.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-bold text-sm uppercase">Smart Reply Suggestions</h4>
                
                {replies.map((reply, index) => (
                  <div key={reply.id} className="border-2 border-border bg-primary/10 dark:bg-primary/5 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <span className="text-xs font-bold text-primary">Option {index + 1}</span>
                        {selectedReply === reply.id && isEditing ? (
                          <textarea
                            value={editedContent}
                            onChange={(e) => setEditedContent(e.target.value)}
                            className="w-full mt-2 p-2 border-2 border-border bg-background text-foreground font-mono text-sm"
                            rows={4}
                          />
                        ) : (
                          <p className="text-sm mt-2 text-foreground">
                            {selectedReply === reply.id && editedContent ? editedContent : reply.draft_content}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-1">
                        {selectedReply === reply.id ? (
                          <>
                            {!isEditing && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEdit(editedContent || reply.draft_content)}
                              >
                                <Edit size={14} />
                              </Button>
                            )}
                            {isEditing && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setIsEditing(false)}
                              >
                                <Check size={14} />
                              </Button>
                            )}
                            <Button
                              size="sm"
                              onClick={handleSend}
                              disabled={isSending}
                              className="bg-green-500 hover:bg-green-600"
                            >
                              <Send size={14} />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleReject(reply.id)}
                            >
                              <X size={14} />
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => handleUseSuggestion(reply.id, reply.draft_content)}
                          >
                            Use
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Actionable Items */}
            {analysis && analysis.actionable_items && analysis.actionable_items.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-bold text-sm uppercase">Action Items</h4>
                {analysis.actionable_items.map((item) => (
                  <div key={item.id} className="p-2 border-2 border-border bg-accent/10 dark:bg-accent/5 text-sm">
                    <span className="font-bold text-foreground">{item.type}:</span> <span className="text-foreground">{item.description}</span>
                    {item.deadline && (
                      <span className="text-xs text-muted-foreground ml-2">
                        Due: {new Date(item.deadline).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
};
