import numpy as np

class GroupedQueryAttention:
    """
    Grouped Query Attention implementation using pure NumPy.
    
    Args:
        d_model: Model dimension (input feature size)
        n_heads: Number of attention heads for queries
        n_kv_heads: Number of key/value heads (groups)
        dropout: Dropout probability (not implemented in pure NumPy)
    """
    def __init__(self, d_model, n_heads, n_kv_heads):
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        
        # Calculate head dimensions
        self.head_dim = d_model // n_heads
        
        # Verify dimensions are compatible
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        assert n_heads % n_kv_heads == 0, "n_heads must be divisible by n_kv_heads"
        
        # Calculate how many query heads share each key/value head
        self.repeats = n_heads // n_kv_heads
        
        # Initialize weight matrices
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weight matrices with Xavier/Glorot initialization."""
        # Query projection: (d_model, d_model)
        self.W_q = np.random.randn(self.d_model, self.d_model) * np.sqrt(2.0 / self.d_model)
        
        # Key projection: (d_model, n_kv_heads * head_dim)
        self.W_k = np.random.randn(self.d_model, self.n_kv_heads * self.head_dim) * np.sqrt(2.0 / self.d_model)
        
        # Value projection: (d_model, n_kv_heads * head_dim)
        self.W_v = np.random.randn(self.d_model, self.n_kv_heads * self.head_dim) * np.sqrt(2.0 / self.d_model)
        
        # Output projection: (d_model, d_model)
        self.W_o = np.random.randn(self.d_model, self.d_model) * np.sqrt(2.0 / self.d_model)
    
    def _split_heads(self, x, n_heads):
        """
        Split the last dimension into (n_heads, head_dim).
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, n_heads * head_dim)
            n_heads: Number of heads to split into
            
        Returns:
            Tensor of shape (batch_size, n_heads, seq_len, head_dim)
        """
        batch_size, seq_len, _ = x.shape
        return x.reshape(batch_size, seq_len, n_heads, self.head_dim).transpose(0, 2, 1, 3)
    
    def _repeat_kv(self, x):
        """
        Repeat key/value heads to match query heads.
        
        Args:
            x: Tensor of shape (batch_size, n_kv_heads, seq_len, head_dim)
            
        Returns:
            Tensor of shape (batch_size, n_heads, seq_len, head_dim)
        """
        batch_size, n_kv_heads, seq_len, head_dim = x.shape
        
        # Expand to add repeat dimension
        x = x[:, :, np.newaxis, :, :]
        
        # Shape: (batch_size, n_kv_heads, repeats, seq_len, head_dim)
        x = np.repeat(x, self.repeats, axis=2)
        
        # Reshape to (batch_size, n_heads, seq_len, head_dim)
        return x.reshape(batch_size, n_kv_heads * self.repeats, seq_len, head_dim)
    
    def _scaled_dot_product_attention(self, Q, K, V, mask=None):
        """
        Compute scaled dot-product attention.
        
        Args:
            Q: Query tensor of shape (batch_size, n_heads, seq_len_q, head_dim)
            K: Key tensor of shape (batch_size, n_heads, seq_len_k, head_dim)
            V: Value tensor of shape (batch_size, n_heads, seq_len_v, head_dim)
            mask: Optional mask tensor
            
        Returns:
            Output tensor and attention weights
        """
        # Compute attention scores: (batch_size, n_heads, seq_len_q, seq_len_k)
        scores = np.matmul(Q, K.transpose(0, 1, 3, 2)) / np.sqrt(self.head_dim)
        
        # Apply mask if provided
        if mask is not None:
            scores = np.where(mask == 0, -1e9, scores)
        
        # Apply softmax to get attention weights
        # Subtract max for numerical stability
        scores_max = np.max(scores, axis=-1, keepdims=True)
        exp_scores = np.exp(scores - scores_max)
        attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        
        # Apply attention weights to values
        output = np.matmul(attention_weights, V)
        
        return output, attention_weights
    
    def _combine_heads(self, x):
        """
        Combine the heads back to original shape.
        
        Args:
            x: Tensor of shape (batch_size, n_heads, seq_len, head_dim)
            
        Returns:
            Tensor of shape (batch_size, seq_len, d_model)
        """
        batch_size, n_heads, seq_len, head_dim = x.shape
        
        # Transpose to (batch_size, seq_len, n_heads, head_dim)
        x = x.transpose(0, 2, 1, 3)
        
        # Reshape to (batch_size, seq_len, d_model)
        return x.reshape(batch_size, seq_len, n_heads * head_dim)
    
    def forward(self, x, mask=None):
        """
        Forward pass of Grouped Query Attention.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Output tensor of shape (batch_size, seq_len, d_model)
        """
        batch_size, seq_len, d_model = x.shape
        
        # Step 1: Linear projections
        # Query projection: (batch_size, seq_len, d_model)
        Q = np.matmul(x, self.W_q)
        
        # Key projection: (batch_size, seq_len, n_kv_heads * head_dim)
        K = np.matmul(x, self.W_k)
        
        # Value projection: (batch_size, seq_len, n_kv_heads * head_dim)
        V = np.matmul(x, self.W_v)
        
        # Step 2: Split into heads
        # Queries: (batch_size, n_heads, seq_len, head_dim)
        Q = self._split_heads(Q, self.n_heads)
        
        # Keys: (batch_size, n_kv_heads, seq_len, head_dim)
        K = self._split_heads(K, self.n_kv_heads)
        
        # Values: (batch_size, n_kv_heads, seq_len, head_dim)
        V = self._split_heads(V, self.n_kv_heads)
        
        # Step 3: Repeat K and V to match Q heads
        # This is the key step in GQA!
        K = self._repeat_kv(K)  # (batch_size, n_heads, seq_len, head_dim)
        V = self._repeat_kv(V)  # (batch_size, n_heads, seq_len, head_dim)
        
        # Step 4: Compute attention
        # Output: (batch_size, n_heads, seq_len, head_dim)
        attention_output, attention_weights = self._scaled_dot_product_attention(Q, K, V, mask)
        
        # Step 5: Combine heads
        # Output: (batch_size, seq_len, d_model)
        combined_output = self._combine_heads(attention_output)
        
        # Step 6: Final linear projection
        # Output: (batch_size, seq_len, d_model)
        output = np.matmul(combined_output, self.W_o)
        
        return output, attention_weights


def demonstrate_gqa():
    """Demonstrate GQA with a simple example."""
    print("=" * 60)
    print("GROUPED QUERY ATTENTION DEMONSTRATION")
    print("=" * 60)
    
    # Configuration
    batch_size = 2
    seq_len = 4
    d_model = 64
    n_heads = 8  # Number of query heads
    n_kv_heads = 2  # Number of key/value heads (groups)
    
    print(f"\nConfiguration:")
    print(f"  Batch size: {batch_size}")
    print(f"  Sequence length: {seq_len}")
    print(f"  Model dimension: {d_model}")
    print(f"  Query heads: {n_heads}")
    print(f"  Key/Value heads: {n_kv_heads}")
    print(f"  Heads per group: {n_heads // n_kv_heads}")
    
    # Create random input
    np.random.seed(42)
    x = np.random.randn(batch_size, seq_len, d_model)
    
    print(f"\nInput shape: {x.shape}")
    
    # Initialize GQA
    gqa = GroupedQueryAttention(d_model, n_heads, n_kv_heads)
    
    # Forward pass
    output, attention_weights = gqa.forward(x)
    
    print(f"\nOutput shape: {output.shape}")
    print(f"Attention weights shape: {attention_weights.shape}")
    
    # Verify memory savings
    print(f"\nMemory Analysis:")
    print(f"  Standard MHA parameters: {d_model * d_model * 3 + d_model * d_model} (Q,K,V,O)")
    print(f"  GQA parameters: {d_model * d_model + d_model * n_kv_heads * gqa.head_dim * 2 + d_model * d_model}")
    print(f"  Reduction ratio: {(1 - (d_model * d_model + d_model * n_kv_heads * gqa.head_dim * 2 + d_model * d_model) / (d_model * d_model * 3 + d_model * d_model)) * 100:.1f}%")
    
    # Show attention pattern
    print(f"\nAttention weights for first batch, first head:")
    print(attention_weights[0, 0])


def step_by_step_explanation():
    """Provide a step-by-step explanation of GQA."""
    print("\n" + "=" * 60)
    print("STEP-BY-STEP EXPLANATION OF GROUPED QUERY ATTENTION")
    print("=" * 60)
    
    steps = [
        {
            "title": "1. Input Preparation",
            "explanation": "We start with input tensor of shape (batch_size, seq_len, d_model). This represents our token embeddings."
        },
        {
            "title": "2. Linear Projections",
            "explanation": "Project input into Query, Key, and Value spaces:\n"
                          "- Q: (batch_size, seq_len, d_model) - all query heads\n"
                          "- K: (batch_size, seq_len, n_kv_heads * head_dim) - fewer heads\n"
                          "- V: (batch_size, seq_len, n_kv_heads * head_dim) - fewer heads"
        },
        {
            "title": "3. Split into Heads",
            "explanation": "Reshape projections into multiple heads:\n"
                          "- Q: (batch_size, n_heads, seq_len, head_dim)\n"
                          "- K: (batch_size, n_kv_heads, seq_len, head_dim)\n"
                          "- V: (batch_size, n_kv_heads, seq_len, head_dim)"
        },
        {
            "title": "4. Group Sharing (Key Step)",
            "explanation": "Repeat K and V heads to match Q heads:\n"
                          "Each K/V head is shared by multiple Q heads\n"
                          "This is the 'grouped' aspect of GQA\n"
                          "Reduces memory while maintaining expressiveness"
        },
        {
            "title": "5. Attention Computation",
            "explanation": "Compute scaled dot-product attention:\n"
                          "scores = Q @ K.T / sqrt(head_dim)\n"
                          "weights = softmax(scores)\n"
                          "output = weights @ V"
        },
        {
            "title": "6. Combine Heads",
            "explanation": "Merge all attention heads back:\n"
                          "From (batch_size, n_heads, seq_len, head_dim)\n"
                          "To (batch_size, seq_len, d_model)"
        },
        {
            "title": "7. Output Projection",
            "explanation": "Final linear transformation to produce output:\n"
                          "output = combined @ W_o\n"
                          "Shape: (batch_size, seq_len, d_model)"
        }
    ]
    
    for step in steps:
        print(f"\n{step['title']}")
        print("-" * len(step['title']))
        print(step['explanation'])


if __name__ == "__main__":
    # Run demonstration
    demonstrate_gqa()
    
    # Show step-by-step explanation
    step_by_step_explanation()
    
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    print("1. GQA reduces memory by sharing K/V heads among Q heads")
    print("2. It's a middle ground between MHA (full) and MQA (minimal)")
    print("3. Maintains most of MHA's performance with less computation")
    print("4. Particularly useful for large models with long sequences")
    print("5. The grouping factor (n_heads // n_kv_heads) controls the trade-off")