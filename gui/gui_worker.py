import threading

class AgentWorker(threading.Thread):
    def __init__(self, query, image_path, max_iter, callback):
        super().__init__()
        self.query = query
        self.image_path = image_path
        self.max_iter = max_iter
        #function to call with progress updates
        self.callback = callback
        self.result = None
        self.running = True
        self.daemon = True #thread dies when main exits
    
    

    def run(self):
        """Execute agent research query in background thread"""
        try:
            from agent import agent_loop, ResearchResponse
            import json

            if self.callback:
                self.callback("Starting research query...", 0)

            #helper function for progress callback
            def progress(iteration, max_iter, msg):
                pct = int((iteration / max_iter) *100)
                if self.callback:
                    self.callback((f"[{iteration}/{max_iter}] {msg}", pct))
            
            #run agent loop
            response_text = agent_loop(
                query=self.query,
                image_path=self.image_path,
                max_iterations=self.max_iter,
                progress_callback=progress
            )

            #parse json response
            try:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                result_dict = json.loads(json_str)
                self.result = ResearchResponse(**result_dict)
            except:
                self.result = ResearchResponse(
                    topic="Error",
                    summary=response_text,
                    sources=[],
                    tools_used=[]
                )
            
            if self.callback:
                self.callback("Complete!", 100)
            
        except Exception as e:
            if self.callback:
                self.callback((f"Error: {str(e)}", -1))
            self.result = None
    

    def stop(self):
        """Signal worker to stop execution"""
        self.running = False
        if self.callback:
            self.callback("Cancelled by user", -1)
        
