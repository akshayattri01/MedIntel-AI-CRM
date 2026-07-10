import { useCallback, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { aiApi } from '../services/api';
import type { AIChatResponse } from '../types';
import type { ChatMessageItem } from '../components/ai/ChatMessage';

type StreamEvent = { type?: string; message?: string; content?: string; delta?: string; payload?: AIChatResponse };

function createId() {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

function createMessage(role: ChatMessageItem['role'], content: string, extra?: Partial<ChatMessageItem>): ChatMessageItem {
  return { id: createId(), role, content, createdAt: new Date().toISOString(), ...extra };
}

function responseText(payload?: AIChatResponse) {
  if (!payload) return '';
  return payload.response;
}

function parseSseChunk(chunk: string) {
  return chunk
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.replace(/^data:\s?/, '').trim())
    .filter(Boolean);
}

async function revealText(text: string, onUpdate: (value: string) => void) {
  let visible = '';
  const chunkSize = text.length > 900 ? 12 : 5;
  for (let index = 0; index < text.length; index += chunkSize) {
    visible += text.slice(index, index + chunkSize);
    onUpdate(visible);
    await new Promise((resolve) => window.setTimeout(resolve, 12));
  }
}

export function useAiAssistant() {
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('Ready');

  const hasMessages = useMemo(() => messages.length > 0, [messages.length]);

  const updateAssistant = useCallback((id: string, patch: Partial<ChatMessageItem>) => {
    setMessages((current) => current.map((message) => (message.id === id ? { ...message, ...patch } : message)));
  }, []);

  const streamResponse = useCallback(async (message: string, assistantId: string) => {
    const response = await aiApi.streamChat(message);
    if (!response.ok || !response.body) throw new Error('Streaming unavailable');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let finalText = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop() ?? '';

      for (const event of events) {
        for (const raw of parseSseChunk(event)) {
          if (raw === '[DONE]') return finalText;
          const parsed = JSON.parse(raw) as StreamEvent;
          if (parsed.type === 'status' && parsed.message) {
            setStatus(parsed.message);
            updateAssistant(assistantId, { status: parsed.message });
          }
          const delta = parsed.delta ?? parsed.content;
          if (delta) {
            finalText += delta;
            updateAssistant(assistantId, { content: finalText, status: undefined });
          }
          if (parsed.type === 'result' && parsed.payload) {
            finalText = responseText(parsed.payload);
          }
        }
      }
    }

    return finalText;
  }, [updateAssistant]);

  const fallbackResponse = useCallback(async (message: string) => {
    const { data } = await aiApi.chat(message);
    return responseText(data);
  }, []);

  const sendMessage = useCallback(async (override?: string) => {
    const outgoing = (override ?? input).trim();
    if (!outgoing || isLoading) return;

    const assistantId = createId();
    setInput('');
    setIsLoading(true);
    setStatus('Connecting to Llama 3.3 70B');
    setMessages((current) => [
      ...current,
      createMessage('user', outgoing),
      { id: assistantId, role: 'assistant', content: '', createdAt: new Date().toISOString(), status: 'Connecting to Llama 3.3 70B', isStreaming: true },
    ]);

    try {
      let text = '';
      try {
        text = await streamResponse(outgoing, assistantId);
      } catch {
        setStatus('Streaming interrupted. Using standard AI response.');
        updateAssistant(assistantId, { status: 'Switching to standard response' });
        text = await fallbackResponse(outgoing);
      }

      if (!text.trim()) text = 'I completed the request, but no response text was returned.';
      updateAssistant(assistantId, { content: '', status: undefined, isStreaming: true });
      await revealText(text, (content) => updateAssistant(assistantId, { content }));
      updateAssistant(assistantId, { isStreaming: false });
      setStatus('Ready');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to reach the AI service.';
      updateAssistant(assistantId, { content: `I could not complete that request. ${message}`, isError: true, isStreaming: false, status: undefined });
      setStatus('Error');
      toast.error('AI request failed');
    } finally {
      setIsLoading(false);
    }
  }, [fallbackResponse, input, isLoading, streamResponse, updateAssistant]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setStatus('Ready');
  }, []);

  return { messages, input, setInput, isLoading, status, hasMessages, sendMessage, clearChat };
}
